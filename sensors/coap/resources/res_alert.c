#include "contiki.h"
#include "coap-engine.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "time.h"
#include "os/dev/leds.h"
#include "sys/etimer.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "poison sensor"
#define LOG_LEVEL LOG_LEVEL_DBG

static bool isActive = false;
static int intensity = 10;

static void res_int_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void post_state_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(alert_actuator,
    "title=\"extractor actuator: ?POST\";obs;rt=\"extractor\"",
    res_int_handler,
    post_state_handler,
    NULL,
    NULL);

static void res_int_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    char msg[300];
    char intensity_str[400];
    int length;

    char myVal = isActive == true ? "T":"N";

    strcpy(msg,"{\"info\":\"");
    strncat(msg,&myVal,1);

    strcat(msg,"\", \"intensity\":\"");
    sprintf(intensity_str, "%d", intensity);

    strcat(msg,intensity_str);
    strcat(msg,"\"}");
    printf("MSG alert: %s\n",msg);
    length = strlen(msg);
    memcpy(buffer, (uint8_t *)msg, length);

    coap_set_header_content_format(response, TEXT_PLAIN);
    coap_set_header_etag(response, (uint8_t *)&length, 1);
    coap_set_payload(response, (uint8_t *)buffer, length);
}

static void post_state_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    if (request != NULL)
    {
        LOG_DBG("POST Request Sent");
    }

    printf("Called Post function");
    size_t len = 0;
    const char *state = NULL;
    int validate = 1;

     // Check if state is defined and valid 
     if((len = coap_get_post_variable(request, "state", &state))) {
         
         // If state is 1 and the LED is currently inactive or the intensity is less than 100, increase intensity by 10 and activate LED 
         if(atoi(state) == 1){
            if(isActive ==true && intensity<=100){
                intensity = intensity + 10;
            }
            leds_set(LEDS_NUM_TO_MASK(LEDS_RED));
            isActive = true;
         }
         // If state is 0 and the LED is active, set isActive to false, intensity to 10 and activate LED 
         else if(atoi(state) == 0){
            leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));
            isActive = false;
            intensity = 10;
         }
         else{
            validate = 0;
         }
     }
     else
     {
        validate = 0;
     }

     if (validate)
     {
        coap_set_status_code(response, CHANGED_2_04);
     }
     else
     {
        coap_set_status_code(response, BAD_REQUEST_4_00);
     }
}