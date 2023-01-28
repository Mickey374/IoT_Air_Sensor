#include "contiki.h"
#include "coap-engine.h"
#include <string.h>
#include "time.h"
#include "os/dev/leds.h"
#include "sys/etimer.h"

/**Config Logs*/
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

static void res_send_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

// uSE THE VALUE TO SET THE COLOR OF THE LEDS
RESOURCE(res_colors,
         "title=\"LEDs: ?color=g|r|y, mode=safe|normal|toxic\";rt=\"Control\"",
         NULL,
         res_send_handler,
         res_send_handler,
         NULL);

static void res_send_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    size_t length = 0;
    const char *state = NULL;
    int success = 1;

    if ((length = coap_get_post_variable(request, "state", &state)))
    {
        LOG_DBG("State %s\n", state);

        if (strncmp(state, "safe", length) == 0)
        {
            leds_set(LEDS_NUM_TO_MASK(LEDS_GREEN));
        }
        else if (strncmp(state, "normal", length) == 0)
        {
            leds_set(LEDS_NUM_TO_MASK(LEDS_YELLOW));
        }
        else if (strncmp(state, "toxic", length) == 0)
        {
            leds_set(LEDS_NUM_TO_MASK(LEDS_RED));
        }
        else
        {
            success = 0;
        }
    }
    else
    {
        success = 0;
    }
    if (!success)
    {
        coap_set_status_code(response, BAD_REQUEST_4_00);
    }
}