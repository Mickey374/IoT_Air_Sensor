#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "contiki.h"
#include "random.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "sys/node-id.h"
#include "os/dev/button-hal.h"
#include "os/dev/serial-line.h"
#include "os/dev/leds.h"

/* Log configuration */
#include "sys/etimer.h"
#include "sys/log.h"

#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_DBG

#define SERVER "coap://[fd00::1]:5683"

static struct etimer register_timer;
bool registered = false;
static int interval = 0;

extern int airquality_value;

/*---------------------------------------------------------------------------*/
void client_chunk_handler(coap_message_t *response)
{
    const uint8_t *chunk;
    if (response == NULL)
    {
        LOG_INFO("Request timed out");
        return;
    }
    if(!registered){
        registered = true;
    }
    int len = coap_get_payload(response, &chunk);
    printf("|%.*s\n", len, (char *)chunk);
}

/*---------------------------------------------------------------------------*/
PROCESS(node, "node");
AUTOSTART_PROCESSES(&node);

int airquality_value = 50;
extern coap_resource_t res_airquality;
extern coap_resource_t res_colors;

PROCESS_THREAD(node, ev, data)
{
    // Set a seed for the random generator as the number of seconds that have elapsed since January 1, 1970
    static coap_endpoint_t server_ep;
    static coap_message_t request[1];

    PROCESS_BEGIN();

    printf("Starting sensor node\n");

    coap_activate_resource(&res_colors, "LEDs");
    coap_activate_resource(&res_airquality, "aqi");

    coap_endpoint_parse(SERVER, strlen(SERVER), &server_ep);

    coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
    coap_set_header_uri_path(request, "registry");


    while (!registered)
    {
        printf("Retrying Registration with Server..\n");
        COAP_BLOCKING_REQUEST(&server_ep, request, client_chunk_handler);
    }

    printf("--Registered--\n");
    etimer_reset(&register_timer, 30*CLOCK_SECOND);

        while (1)
    {
        PROCESS_WAIT_EVENT();

        if (ev == PROCESS_EVENT_TIMER && data == &register_timer)
        {
            // returns a random integer between 0 and
            airquality_value = rand() % 201;
            res_airquality.trigger();
            interval++;
            etimer_reset(&register_timer);
        }
    }
    PROCESS_END();
}