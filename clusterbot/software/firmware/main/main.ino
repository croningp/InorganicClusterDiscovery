#include <CommandHandler.h>
#include <CommandManager.h>
CommandManager cmdMgr;

/* Include the base files needed such as Accel Stepper, Servo etc */
#include <AccelStepper.h>
#include <LinearAccelStepperActuator.h>

/* Include the "Command" version of the above */
#include <CommandAccelStepper.h>
#include <CommandLinearAccelStepperActuator.h>

#include <CommandAnalogWrite.h>


/* Set up the base objects and Command objects */
AccelStepper stepperX(AccelStepper::DRIVER, 54, 55);
CommandLinearAccelStepperActuator X(stepperX, 3, 38);

AccelStepper stepperY(AccelStepper::DRIVER, 60, 61);
CommandLinearAccelStepperActuator Y(stepperY, 14, 56);

AccelStepper stepperZ(AccelStepper::DRIVER, 46, 48);
CommandLinearAccelStepperActuator Z(stepperZ, 18, 62);

AccelStepper stepperE0(AccelStepper::DRIVER, 26, 28);
CommandLinearAccelStepperActuator E0(stepperE0, 2, 24);

AccelStepper stepperE1(AccelStepper::DRIVER, 36, 34);
CommandLinearAccelStepperActuator E1(stepperE1, 15, 30);


CommandAnalogWrite PWM(8);
CommandAnalogWrite stirrer(9);


void setup() {
    Serial.begin(115200); // Always 115200

    /* Register devices to the command manager */
    X.registerToCommandManager(cmdMgr, "wheel"); 
    Y.registerToCommandManager(cmdMgr, "pH");
    Z.registerToCommandManager(cmdMgr, "R1");
    E0.registerToCommandManager(cmdMgr, "R2"); 
    E1.registerToCommandManager(cmdMgr, "R3"); 
    
    PWM.registerToCommandManager(cmdMgr, "A1");
    stirrer.registerToCommandManager(cmdMgr, "A2");

    cmdMgr.init();

}

void loop() {
    cmdMgr.update();
}
