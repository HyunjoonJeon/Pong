/*
 * "Hello World" example.
 *
 * This example prints 'Hello from Nios II' to the STDOUT stream. It runs on
 * the Nios II 'standard', 'full_featured', 'fast', and 'low_cost' example
 * designs. It runs with or without the MicroC/OS-II RTOS and requires a STDOUT
 * device in your system's hardware.
 * The memory footprint of this hosted application is ~69 kbytes by default
 * using the standard reference design.
 *
 * For a reduced footprint version of this template, and an explanation of how
 * to reduce the memory footprint for a given application, see the
 * "small_hello_world" template.
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "system.h"
#include "altera_up_avalon_accelerometer_spi.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "altera_avalon_pio_regs.h"
#include "sys/alt_irq.h"
#include <stdlib.h>

#define OFFSET -32
#define PWM_PERIOD 16

alt_8 pwm = 0;
alt_u8 led;
int level;
int filter_slot=0;
double filter[5]={0,0,0,0,0};

void led_write(alt_u8 led_pattern) {
    IOWR(LED_BASE, 0, led_pattern);
}

void convert_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

void sys_timer_isr() {
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);

    if (pwm < abs(level)) {

        if (level < 0) {
            led_write(led << 1);
        } else {
            led_write(led >> 1);
        }

    } else {
        led_write(led);
    }

    if (pwm > PWM_PERIOD) {
        pwm = 0;
    } else {
        pwm++;
    }

}

void timer_init(void * isr) {

    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0003);
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_BASE, 0x0900);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_BASE, 0x0000);
    alt_irq_register(TIMER_IRQ, 0, isr);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0007);

}

double filtering(alt_32 current_value){
	double result=0;
	filter[filter_slot]=current_value;
	for(int i=0; i<5;i++){
		result += filter[i]/5;
		printf("Array data: %f \n", filter[i]);
	}
	if (filter_slot<4){
		filter_slot++;
	}else{
		filter_slot=0;
	}
	return result;
}

int main() {
	double filtered_data;
	alt_32 x_read, y_read;
    alt_up_accelerometer_spi_dev * acc_dev;
    acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
    if (acc_dev == NULL) { // if return 1, check if the spi ip name is "accelerometer_spi"
        return 1;
    }

    timer_init(sys_timer_isr);

	printf("Running..\n");
	FILE* fp;
	char prompt = 0;

	// create file pointer to jtag_uart port
	fp = fopen ("/dev/jtag_uart", "r+");

	if (fp) {
		while (prompt != 's')
		{
			prompt = getc(fp);
			if(prompt == 'x')
			{
				alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
				alt_printf("Raw data: %x \n", x_read);
				convert_read(x_read, & level, & led);
				filtered_data = filtering(x_read);
				printf("Filtered data: <--> %f <-->\n", filtered_data);
			}
			else if (prompt == 'y')
			{
				alt_up_accelerometer_spi_read_y_axis(acc_dev, & y_read);
				alt_printf("Raw data: <--> %x <-->\n ", y_read);
				convert_read(y_read, & level, & led);
			}else alt_printf("Raw data: <--> <-->\n");
		}
		fprintf(fp, "Closing the JTAG UART file handle.\n %c",0x4);
		fclose(fp);
	}
	printf("Complete\n");

	return 0;
}
