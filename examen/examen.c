#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"
#include "driverlib/pwm.h"
#include "driverlib/timer.h" 

uint32_t clock;

int main(void)
{
    uint32_t pwm_period = 6000;
    uint8_t velocidad = 75;
    uint8_t estado_motor = 0; 
    uint32_t pulse;

    
    
    uint32_t tiempo_ticks;
    float microsegundos;
    float distancia;

    clock = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480), 120000000);

    //PERIFERICOS
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART7);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOC);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOL);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOM);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOK);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0); 

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));

    
    // TIMER 0 
    TimerConfigure(TIMER0_BASE, TIMER_CFG_ONE_SHOT); 

    // Botones (PJ0, PJ1), Motores ini(PL0-PL3), Trig (PL4), Echo (PM0), Buzzer (PM1)
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, 0x03); // PJ0 y PJ1
    GPIOPadConfigSet(GPIO_PORTJ_BASE, 0x03, GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);
    
    // Motores ini y Trig 
    GPIOPinTypeGPIOOutput(GPIO_PORTL_BASE, 0x1F); 
    //buzzer
    GPIOPinTypeGPIOInput(GPIO_PORTM_BASE, 0x01); 
    //echo
    GPIOPinTypeGPIOOutput(GPIO_PORTM_BASE, 0x02); 
    
    // PWM (PK4, PK5)
    GPIOPinConfigure(GPIO_PK4_M0PWM6);
    GPIOPinConfigure(GPIO_PK5_M0PWM7);
    GPIOPinTypePWM(GPIO_PORTK_BASE, 0x30);
    
    PWMGenConfigure(PWM0_BASE, PWM_GEN_3, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_3, pwm_period);
    PWMOutputState(PWM0_BASE, PWM_OUT_6_BIT | PWM_OUT_7_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_3);

    while(1)
    {
        // 2. BOTONES
        if(GPIOPinRead(GPIO_PORTJ_BASE, 0x01) == 0) { 
            estado_motor = 1;
            GPIOPinWrite(GPIO_PORTL_BASE, 0x05, 0x05); 
            pulse = (pwm_period * velocidad) / 100;
            PWMPulseWidthSet(PWM0_BASE, PWM_OUT_6, pulse);
            PWMPulseWidthSet(PWM0_BASE, PWM_OUT_7, pulse);
        }
        if(GPIOPinRead(GPIO_PORTJ_BASE, 0x02) == 0) { 
            estado_motor = 0;
            PWMPulseWidthSet(PWM0_BASE, PWM_OUT_6, 0);
            PWMPulseWidthSet(PWM0_BASE, PWM_OUT_7, 0);
            GPIOPinWrite(GPIO_PORTL_BASE, 0x0F, 0x00); 
        }

        // 3. ULTRASONICO CON TIMER 
        if(estado_motor == 1)
        {
            GPIOPinWrite(GPIO_PORTL_BASE, 0x10, 0x10); 
            SysCtlDelay((clock/3000000)*10);
            GPIOPinWrite(GPIO_PORTL_BASE, 0x10, 0x00);

            while(GPIOPinRead(GPIO_PORTM_BASE, 0x01) == 0); 

            TimerLoadSet(TIMER0_BASE, TIMER_A, 0xFFFFFFFF);
            TimerEnable(TIMER0_BASE, TIMER_A);

            while(GPIOPinRead(GPIO_PORTM_BASE, 0x01) != 0);

            TimerDisable(TIMER0_BASE, TIMER_A);
            tiempo_ticks = 0xFFFFFFFF - TimerValueGet(TIMER0_BASE, TIMER_A);
            
            microsegundos = (float)tiempo_ticks * 1000000.0f / (float)clock;
            distancia = (microsegundos * 0.0343f) / 2.0f;

            if(distancia > 0 && distancia <= 5.0f)
            {
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_6, 0);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_7, 0);
                GPIOPinWrite(GPIO_PORTL_BASE, 0x0F, 0x00); 
                GPIOPinWrite(GPIO_PORTL_BASE, 0x09, 0x09); 
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_6, pulse);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_7, pulse);
                SysCtlDelay((clock/3)*0.5);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_6, 0);
                PWMPulseWidthSet(PWM0_BASE, PWM_OUT_7, 0);
                GPIOPinWrite(GPIO_PORTL_BASE, 0x0F, 0x00); 
                
            }
        }
    }
}