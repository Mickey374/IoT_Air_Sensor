#include "contiki.h"
#include "coap-engine.h"
#include "dev/leds.h"
#include <string.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

static void rest_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);


RESOURCE(res_leds,
        "title=\"LEDs: ?color=r|g|y, POST/PUT mode=good|moderate|unhealthy\";rt=\"Control\"",
        NULL,
        rest_post_put_handler,
        rest_post_put_handler,
        NULL
        );

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    size_t len = 0;
    int success = 1;
    const char *mode = NULL;

     if((len = coap_get_post_variable(request, "mode", &mode))) {
    LOG_DBG("mode %s\n", mode);


    if(strncmp(mode, "good", len) == 0) {
         leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));
    } else if(strncmp(mode, "moderate", len) == 0) {
         leds_set(LEDS_NUM_TO_MASK(LEDS_YELLOW));
    } else if(strncmp(mode, "unhealthy", len) == 0) {
         leds_set(LEDS_NUM_TO_MASK(LEDS_RED));
    } else {
         success = 0;
    }
  } else {
    success = 0;
  } 
  if(!success) {
    coap_set_status_code(response, BAD_REQUEST_4_00);
  }
}