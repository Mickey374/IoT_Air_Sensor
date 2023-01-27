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
#define EVENT_INTERVAL 30

static bool isDetected = false;
static bool isActive = false;
static int intensity = 10;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);

EVENT_RESOURCE(poison_sensor,
            "title=\'Poison sensor: ?POST\';obs",
            res_get_handler,
            NULL,
            NULL,
            NULL,
            res_event_handler);

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    int length;
    char msg[300];

    if(isActive==true && intensity<=100){
        intensity=intensity+10;
    }
    else if(isActive==false){
        intensity=10;
    }

    if(isDetected==1){
        isActive=true;
    }
    else if (isDetected==0){
        isActive=false;
    }

    char val1 = isActive == 1 ? 'T': 'N';  // If isActive is true assign val1 to 'T', otherwise assign it to 'N' 
    char val2 = isDetected == 1 ? 'T': 'N'; // If isDetected is true assign val2 to 'T', otherwise assign it to 'N'

    strcpy(msg,"{\"isDetected\":\"");   // Copy "{"isDetected":" into msg string 
    strncat(msg,&val2,1);              // Concatenate val2 onto msg string  (val2 will be either T or N)  
    strcat(msg,"\", \"info\":\"");     // Concatenate ", "info":" onto msg string  

    strncat(msg,&val1,1);              // Concatenate val1 onto msg string (val1 will be either T or N)  
    strcat(msg,"\", \"intensity\":\"");// Concatenate ", "intensity":" onto msg string 

    char intensity_str[400];           // Create a new character array called intensity_str with a size of 400 characters 
    sprintf(intensity_str, "%d", intensity);  // Convert integer intensity into a string and store it in intensity_str array 
    strcat(msg,intensity_str);         // Concatenate contents of intensity_str onto msg string  
    strcat(msg,"\"}");                 // Concatenate "}" onto end of msg string

    length = strlen(msg);              // Store length of entire msg string in length variable 

    memcpy(buffer, (uint8_t *)msg, length);  // Copy contents of msg into buffer array as type uint8* (unsigned 8 bit integer) 
    printf("MSG res poison_sensor send : %s\n", msg);// Print out contents of entire message for debugging purposes 

    coap_set_header_content_format(response, TEXT_PLAIN);
    coap_set_header_etag(response, (uint8_t *)&length, 1);
    coap_set_payload(response, (uint8_t *)buffer, length);
}

static void res_event_handler(void) {
    bool new_isDetected = isDetected;

    srand(time(NULL));  // Set random seed with current time
    int random = rand() % 2;  // Generate random number between 0 and 1

    if (random == 0) { // Generate random number between 0 and 1 
        new_isDetected = !isDetected; // Flip value of isDetected 
    }

    if (new_isDetected != isDetected) {  // Check if value of isDetected has changed since last check
        isDetected = new_isDetected;  // Update value of isDetected accordingly
        coap_notify_observers(&motion_sensor);  // Notify all observers of change in state
    }
}