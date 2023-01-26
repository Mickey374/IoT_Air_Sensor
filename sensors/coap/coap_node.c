#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "contiki.h"
#include "random.h"
#include "net/routing/routing.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "sys/node-id.h"
#include "os/dev/button-hal.h"
#include "os/dev/serial-line.h"
#include "os/dev/leds.h"
// #include "node-id.h"
// #include "dev/button-hal.h"

/* Log configuration */
#include "sys/etimer.h"
#include "sys/log.h"

#define LOG_MODULE "NODE"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_CLIENT_PORT	8765
#define UDP_SERVER_PORT	5678

#define SERVER_EP "coap://[fd00::1]:5683"
#define SERVER_REGISTRATION "registration"

#define SENSOR_TYPE "poison_sensor"
#define SIMULATION_INTERVAL 30
#define TOGGLE_INTERVAL 10
#define TIMEOUT_INTERVAL 30

static struct etimer register_timer;
static struct etimer simulation;
static struct etimer timeout_timer;

bool registered = false;
bool btnPressed = false;

extern coap_resource_t poison_sensor;
extern coap_resource_t alert_actuator;

PROCESS(coap_client, "CoAP Client");
PROCESS(sensor_node, "Sensor node");
AUTOSTART_PROCESSES(&coap_client, &sensor_node);

/*---------------------------------------------------------------------------*/
void response_handler(coap_message_t *response){
    const uint8_t *chunk;
    if(response == NULL) {
        puts("Request timed out");
        return;
    }
    int len = coap_get_payload(response, &chunk);
    printf("|%.*s\n", len, (char *)chunk);
}
/*---------------------------------------------------------------------------*/

PROCESS_THREAD(coap_client, ev, data){
    static coap_endpoint_t server_ep;
    static coap_message_t request[1];
    uip_ipaddr_t dest_ipaddr; 

    PROCESS_BEGIN();
    coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);

    etimer_set(&register_timer, TOGGLE_INTERVAL * CLOCK_SECOND);

    while (1)
    {
        PROCESS_YIELD();

        if((ev == PROCESS_EVENT_TIMER && data == &register_timer) || ev == PROCESS_EVENT_POLL) {
            if(NETSTACK_ROUTING.node_is_reachable() && NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)){
                printf("Registration phase\n");

                coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
                coap_set_header_uri_path(request, (const char *)&SERVER_REGISTRATION);
                char msg[255];
                strcpy(msg, "{\"Resource\":\"poison_resource\"}");
                
                printf("MSG registration coap_node : %s\n", msg);
                coap_set_payload(request, (uint8_t*) msg, strlen(msg));
                COAP_BLOCKING_REQUEST(&server_ep, request, response_handler);
                registered = true;
                leds_toggle(LEDS_GREEN);
                break;
            }

            else{
                printf("No RPL Address Received...\n");
            }
            etimer_reset(&register_timer);
        }
    }
    LOG_INFO("REGISTERED\nStarting Poisonous Gas Sensor Server\n");
    PROCESS_END();
}

PROCESS_THREAD(sensor_node, ev, data){
    button_hal_button_t *btn;

    PROCESS_BEGIN();
    coap_activate_resource(&poison_sensor, "poison_resource");
    coap_activate_resource(&alert_actuator, "alert_actuator");

    btn = button_hal_get_by_index(0);

    etimer_set(&simulation, CLOCK_SECOND * SIMULATION_INTERVAL);
    LOG_INFO("Simulation Started...\n");

    while (1)
    {
        PROCESS_YIELD();

        if (ev==PROCESS_EVENT_TIMER && data ==&simulation && !btnPressed)
        {
            printf("Poisonous Gas sensed\n");
            poison_sensor.trigger();
            etimer_set(&simulation, CLOCK_SECOND * SIMULATION_INTERVAL);
        }
        if (ev==button_hal_press_event)
        {
            if (registered)
            {
                if (!btnPressed)
                {
                    printf("Button Pressed...\n");
                    btn = (button_hal_button_t *)data;
                    printf("Release Event (%s)\n", BUTTON_HAL_GET_DESCRIPTION(btn));
                    btnPressed = true;
                    etimer_set(&timeout_timer,TIMEOUT_INTERVAL*CLOCK_SECOND);
                }
                else
                {
                    etimer_stop(&timeout_timer);
                    printf("Stop Extractor\n");
                    btnPressed = false;
                }
            }
        }
    }
}