/* "Hello World" example.
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
static alt_u8 segments[20] = {
    0x40, 0x79, 0x24, 0x30, 0x19, 0x12, 0x2, 0x78, 0x0, 0x18, 		  /* 0-9 */
    0x3F, 0x8, 0x9, 0x47, 0x71, 0x6, 0x3F};						  /* "-" and A H L - E */

//The decimal point still shows up, it can probably be handled later


static void sevenseg_set_hex0(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, data);
}

static void sevenseg_set_hex1(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, data);
}

static void sevenseg_set_hex2(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, data);
}

static void sevenseg_set_hex3(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, data);
}

static void sevenseg_set_hex4(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, data);
}

static void sevenseg_set_hex5(alt_u8 hex)
{
  alt_u32 data = segments[hex & 15] | (segments[(hex >> 4) & 15] << 8);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, data);
}

static void sevenseg_turn_off()
{
  IOWR_ALTERA_AVALON_PIO_DATA(HEX0_BASE, 0xffff);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX1_BASE, 0xffff);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX2_BASE, 0xffff);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX3_BASE, 0xffff);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX4_BASE, 0xffff);
  IOWR_ALTERA_AVALON_PIO_DATA(HEX5_BASE, 0xffff);
}


static void sevenseg_say_hello()
{
  sevenseg_set_hex4(12);
  sevenseg_set_hex3(15);
  sevenseg_set_hex2(13);
  sevenseg_set_hex1(13);
  sevenseg_set_hex0(0);
}

static void sevenseg_home_player()
{
	sevenseg_set_hex5(12);
}

static void sevenseg_away_player()
{
	sevenseg_set_hex5(11);
}

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
		//printf("Array data: %f \n", filter[i]);
	}
	printf("Single reading from array: %f \n", filter[4]);
	//IOWR(HEX0_BASE, 0, '8');
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

    sevenseg_say_hello();
    usleep(300000);
    sevenseg_home_player();
    usleep(300000);
    sevenseg_away_player();
    usleep(900000);

    sevenseg_turn_off();		//turn off display
    usleep(900000);				//sleep for about 3 seconds
    sevenseg_set_hex2(0);		//home player
    sevenseg_set_hex0(0);		//away player
    sevenseg_set_hex1(10);		//dash in between the numbers

	printf("Running..\n");
	FILE* fp;
	char prompt = 0;

	// create file pointer to jtag_uart port
	fp = fopen ("/dev/jtag_uart", "r+");

	for(int i = 0; i <= 16; i++)
	{
		sevenseg_set_hex0(i);
		sevenseg_set_hex2(i);
		usleep(300000);		//sleep for about one second
	}

	sevenseg_set_hex2(0);		//home player
	sevenseg_set_hex0(0);		//away player
	sevenseg_set_hex1(10);		//dash in between the numbers

	prompt = 'x';
	if (fp) {
		while (prompt != 's')
		{
			prompt = getc(fp);

			switch(prompt)
			{
				case 'x':
				{
					alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
					alt_printf("Raw data: %x \n", x_read);
					convert_read(x_read, & level, & led);
					filtered_data = filtering(x_read);
					printf("Filtered data: <--> %f <-->\n", filtered_data);
					alt_printf("==========\nReceiving x-axis update command \n==========\n");
					break;
				}
				case 'y':
				{
					alt_up_accelerometer_spi_read_y_axis(acc_dev, & y_read);
					alt_printf("Raw data: <--> %x <-->\n ", y_read);
					convert_read(y_read, & level, & led);
					alt_printf("==========\nReceiving x-axis update command \n==========\n");
					break;
				}
				case '1':	//this is for the home player
				{
					sevenseg_set_hex2(1);
					alt_printf("==========\nReceiving score update (home) command \n==========\n");
					break;
				}
				case '2':
				{
					sevenseg_set_hex2(2);
					alt_printf("==========\nReceiving score update (home) command \n==========\n");
					break;
				}
				case '3':
				{
					sevenseg_set_hex2(3);
					alt_printf("==========\nReceiving score update (home) command \n==========\n");
					break;
				}
				case '4':
				{
					sevenseg_set_hex2(4);
					alt_printf("==========\nReceiving score update (home) command \n==========\n");
					break;
				}
				case '5':
				{
					sevenseg_set_hex2(5);
					alt_printf("==========\nReceiving score update (home) command \n==========\n");
					break;
				}
				case '6':	//this is for the away player
				{
					sevenseg_set_hex0(1);
					alt_printf("==========\nReceiving score update (away) command \n==========\n");
					break;
				}
				case '7':
				{
					sevenseg_set_hex0(2);
					alt_printf("==========\nReceiving score update (away) command \n==========\n");
					break;
				}
				case '8':
				{
					sevenseg_set_hex0(3);
					alt_printf("==========\nReceiving score update (away) command \n==========\n");
					break;
				}
				case '9':
				{
					sevenseg_set_hex0(4);
					alt_printf("========== \n Receiving a score update (away) command \n ========= \n");

					break;
				}
				case '0':
				{
					sevenseg_set_hex0(5);
					alt_printf("==========\nReceiving score update (away) command \n==========\n");
					break;
				}
				case'c':
				{
					sevenseg_turn_off();		//turn off display
					//usleep(900000);			//sleep for about 3 seconds
					sevenseg_set_hex2(0);		//home player
					sevenseg_set_hex0(0);		//away player
					sevenseg_set_hex1(10);		//dash in between the numbers
					alt_printf("==========\nReceiving clean command \n==========\n");
					break;
				}
				case 'h':
				{
					sevenseg_home_player();
					alt_printf("==========\nReceiving home player command \n==========\n");
					break;
				}
				case 'a':
				{
					sevenseg_away_player();
					alt_printf("==========\nReceiving away player command \n==========\n");
					break;
				}
				default:
				{
					alt_printf("Raw data: <--> <-->\n");
					break;
				}
			}
		}
		fprintf(fp, "Closing the JTAG UART file handle.\n %c",0x4);
		fclose(fp);
	}
	printf("Complete\n");

	return 0;
}
