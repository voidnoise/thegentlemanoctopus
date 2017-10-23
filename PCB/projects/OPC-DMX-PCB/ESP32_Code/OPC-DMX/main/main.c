#include "freertos/FreeRTOS.h"
#include "esp_wifi.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "esp_event.h"
#include "esp_event_loop.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/rmt.h"
#include "esp_eth.h"
#include "esp_log.h"

#include "pixel_interface.h"
esp_err_t event_handler(void *ctx, system_event_t *event)
{
    return ESP_OK;
}

esp_err_t pixel_test_init(void)
{

    pixel_channel_config_t test_channel;
	test_channel.gpio_output_pin = GPIO_NUM_4;
	test_channel.rmt_channel = RMT_CHANNEL_0;
	test_channel.channel_length = 7;
	test_channel.pixel_channel = PIXEL_CHANNEL_0;

	pixel_init_rmt_channel(&test_channel);

	printf("rmt initialised\n");

	pixel_create_data_buffer(&test_channel);

	for(uint32_t i=0; i < test_channel.channel_length; i++)
	{
		test_channel.pixels[i].r = i;
		test_channel.pixels[i].g = i+1;
		test_channel.pixels[i].b = i+2;
		test_channel.pixels[i].w = i+3;
		printf("r = %d g = %d b = %d w = %d \n", test_channel.pixels[i].r, test_channel.pixels[i].g, test_channel.pixels[i].b, test_channel.pixels[i].w);
	}

	return ESP_OK;
}

void app_main(void)
{
    printf("Hello world!\n");

    /* Print chip information */
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    printf("This is ESP32 chip with %d CPU cores, WiFi%s%s, ",
            chip_info.cores,
            (chip_info.features & CHIP_FEATURE_BT) ? "/BT" : "",
            (chip_info.features & CHIP_FEATURE_BLE) ? "/BLE" : "");

    printf("silicon revision %d, ", chip_info.revision);

    printf("%dMB %s flash\n", spi_flash_get_chip_size() / (1024 * 1024),
            (chip_info.features & CHIP_FEATURE_EMB_FLASH) ? "embedded" : "external");

    printf("Starting\n");

    pixel_test_init();



    /* loop */
    for(;;){}



}

