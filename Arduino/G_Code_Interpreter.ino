/*
Bailey Sauter 
ECE 342
G Code Interpreter

Example G Codes:
Multiple work if format is command \ncommand

G0 X10 Y15 Z5
G0 X10 Y15 Z-5
G0 X100 Y50 Z0

G1 X-10 Y15 Z5
G1 X-10 Y15 Z-5
G1 X100 Y-50 Z0

G20
G21
G90
G91
M02
M06

If linear motions not smooth enough, try combing old algorithm for continuous movement
(stored in OneNote) with new intermediate points algorithm
*/

//Includes and Defines
//#include <TMCStepper.h>

//Stepper Driver Definitions
#define EN_PIN           10 // Enable
#define DIR_PIN1          8 // Direction
#define STEP_PIN1         9 // Step
#define DIR_PIN2          2
#define STEP_PIN2         3
#define DIR_PIN3          4
#define STEP_PIN3         5
#define MS1               13 // Software Master Out Slave In (MOSI)
#define MS2               12 // Software Master In Slave Out (MISO)



//Variable Definitions
int currentcode;
float currentx;
float currenty;
float desiredx;
float desiredy;
float desiredz;
float currentangle1 = 0;
float currentangle2 = 0;
float desiredangle1;
float desiredangle2;
int steps1;
int steps2;
int steps3;
float L1 = 150; //First link
float L2 = 150; //Second link
float L3; //Imaginary link connecting base to tip
bool units = true; //Default is mm (true), if changed to in (false) must receive G20 command (G21 to revert back)
bool absolutemode = true; //Default is absolute mode, G91 changes to incremental mode, G90 changes back

void setup() {

  pinMode(EN_PIN, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(STEP_PIN1, OUTPUT);
  pinMode(DIR_PIN1, OUTPUT);
  pinMode(STEP_PIN2, OUTPUT);
  pinMode(DIR_PIN2, OUTPUT);
  pinMode(STEP_PIN3, OUTPUT);
  pinMode(DIR_PIN3, OUTPUT);
  digitalWrite(EN_PIN, LOW);      // Enable driver in hardware
  digitalWrite(MS1, HIGH);        // Set MS1:2 to desired microstep setting
  digitalWrite(MS2, HIGH);        // 00: 1/8, 01: 1/2, 10: 1/4, 11: 1/16
  
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  //Ask for G code input:
  Serial.println("Waiting for G Code Command:");
}

void takeinstructions() {
  //Get any incoming characters:
  if (Serial.available() > 0) {
    
    char thisChar = Serial.read();
    String command = "";

    if( thisChar == 'G' ){    // Check for G code
      
      Serial.println("You sent a G command");
      command = "";

      while( thisChar != ' ' && thisChar != '\n' ){ //Check for specific G code following 'G'

        thisChar = Serial.read();
        command += thisChar;
      }

      currentcode = command.toInt();
      Serial.print( "You sent G code command: G" );
      Serial.println( command );
      
      while(thisChar == ' ' && thisChar != '\n' ){ //Loop disregards spaces

        thisChar = Serial.read();
      }

      if( thisChar == 'X' ){ //Check for X coordinate

        command = "";

        while( thisChar != ' ' ){ //Read X coordinate

          thisChar = Serial.read();
          command += thisChar;
        }
   
        desiredx = command.toInt(); //Store X desired coordinate

        if( !units ){

          desiredx = desiredx * 25.4; //If units is set to inches converts input to mm for interpretation
        }

        if( !absolutemode ){

          desiredx += currentx;
        }
        
        Serial.print("X coordinate: ");
        Serial.println( command );
      }

      while(thisChar == ' '){ //Loop disregards spaces

        thisChar = Serial.read();
      }
      
      if( thisChar == 'Y' ){ //Check for Y coordinate

        command = "";

        while( thisChar != ' ' && thisChar != '\n'){ //Read Y coordinate

          thisChar = Serial.read();
          command += thisChar;
        }

        desiredy = command.toInt(); //Store desired Y coordinate

        if( !units ){

          desiredy = desiredy * 25.4; //If units is set to inches converts input to mm for interpretation
        }

        if( !absolutemode ){

          desiredy += currenty;
        }
        
        Serial.print("Y coordinate: ");
        Serial.println( command );
      }

      while(thisChar == ' '){ //Loop disregards spaces

        thisChar = Serial.read();
      }

      if( thisChar == 'Z' ){ //Check for Y coordinate

        command = "";

        while( thisChar != ' ' && thisChar != '\n'){ //Read Y coordinate

          thisChar = Serial.read();
          command += thisChar;
        }

        desiredz = command.toInt(); //Store desired Y coordinate

        if( !units ){

          desiredy = desiredy * 25.4; //If units is set to inches converts input to mm for interpretation
        }

        if( !absolutemode ){

          desiredy += currenty;
        }
        
        Serial.print("Z coordinate: ");
        Serial.println( command );
      }

      if( currentcode == 0 || currentcode == 1 ){

         cartesiantopolar(); //Convert input desired x and y to desired angles
      }
     
      followinstructions(); //Executes the desired instructions stated in last function based on G code 
      currentangle1 = desiredangle1;
      currentangle2 = desiredangle2; //Updates the current angle settings
      currentx = desiredx; //Updates the current x and y 
      currenty = desiredy;

      Serial.print( "Your current angle #1 = " );
      Serial.println( currentangle1 );
      Serial.print( "Your current angle #2 = " );
      Serial.println( currentangle2 );
      Serial.print( "Your current X coordinate = " );
      Serial.println( currentx );
      Serial.print( "Your current Y coordinate = " );
      Serial.println( currenty );
      Serial.println();
      
      return;
      
    }else if(thisChar == 'M' ){
      
      Serial.println("You sent an M command");

      while( thisChar != ' ' && thisChar != '\n' ){ //Check for specific G code following 'M'

        thisChar = Serial.read();
        command += thisChar;
      }

      currentcode = command.toInt();
      Serial.print( "You sent M code command: M" );
      Serial.println( command );

      followinstructions();

      currentangle1 = desiredangle1;
      currentangle2 = desiredangle2; //Updates the current angle settings
      currentx = desiredx; //Updates the current x and y 
      currenty = desiredy;

      Serial.print( "Your current angle #1 = " );
      Serial.println( currentangle1 );
      Serial.print( "Your current angle #2 = " );
      Serial.println( currentangle2 );
      Serial.print( "Your current X coordinate = " );
      Serial.println( currentx );
      Serial.print( "Your current Y coordinate = " );
      Serial.println( currenty );
      Serial.println();
      
      return;
      
    }else{
      
      Serial.print("Not a G Code command");
      Serial.println();
      return;
    }
  }
}

void cartesiantopolar(){ //Takes desired x and y and converts to desired angles

  Serial.print( "Your desired X coordinate is: " );
  Serial.println( desiredx );
  Serial.print( "Your desired Y coordinate is: " );
  Serial.println( desiredy );
  Serial.print( "Your desired Z coordinate is: " );
  Serial.println( desiredz );
  
  L3 = sqrt( (desiredx * desiredx ) + (desiredy * desiredy) ); //Pythagorean Theorem

  Serial.print( "Your imaginary link L3 is: ");
  Serial.println( L3 );

  if( L3 != 0 ){ //Makes sure that it doesn't try to divide by zero
    
    float alpha = acos( ( (L1 * L1) + (L3 * L3) - (L2 * L2) ) / (2 * L1 * L3) ); //Law of cosines to find angle between L1 and L3
    desiredangle1 = (alpha + atan( desiredy / desiredx )) * 57.2957795;  //Find desired angle of first motor (assumes 0 deg is X axis)and puts in degrees
  
    float beta = acos( ( (L1 * L1) + (L2 * L2) - (L3 * L3) ) / (2 * L1 * L2) ); //Law of cosines to find angle between L1 and L2
    desiredangle2 = beta * 57.2957795; //Find desired angle of second motor (assumes 0 deg is flush with right side of L1) and puts in degrees
    
  }else{
  
    desiredangle1 = 0;
    desiredangle2 = 0;
  }

  //Checks for negative coordinates, adjusts angles accordingly
  if( desiredx < 0 && desiredy < 0 ){

    desiredangle1 += 180;
    
  }else if( desiredx < 0 && desiredy >= 0 ){

    desiredangle1 = 180 - desiredangle1;
    desiredangle2 = 360 - desiredangle2;
    
  }else if( desiredx >= 0 && desiredy < 0 ){

    desiredangle1 = 360 - desiredangle1;
    desiredangle2 = 360 - desiredangle2;
  }
  

  Serial.print( "Your desired angle of L1 is: ");
  Serial.println( desiredangle1 );
  Serial.print( "Your desired angle of L2 is: ");
  Serial.println( desiredangle2 );

  float angledifference1 = desiredangle1 - currentangle1; //Calculates the difference between desired angle and current angle (the amount of angle it needs to move)
  float angledifference2 = desiredangle2 - currentangle2;

  if( angledifference1 > 180 ){ //Checks to see if negative route will be faster

    angledifference1 = -1 * (360 - angledifference1);
  }
  if( angledifference2 > 180 ){

    angledifference2 = -1 * (360 - angledifference2);
  }

  steps1 = 8.88 * angledifference1; //Calculates the amount of steps that each motor needs to move to achieve proper angle
  steps2 = 8.88 * angledifference2; //Assumes NEMA 17 motors with 200 steps/rev microstepped by 1/16 so 8.88 microsteps per degree
  steps3 = desiredz;

  //Informs user of desired action so that they can check against actual action
  if( steps1 >= 0 ){

    Serial.print("Stepper #1 needs to take ");
    Serial.print(steps1);
    Serial.println(" steps in the positive direction");
    
  }else{

    Serial.print("Stepper #1 needs to take ");
    Serial.print(abs(steps1));
    Serial.println(" steps in the negative direction");
        
  }
  if( steps2 >= 0 ){

    Serial.print("Stepper #2 needs to take ");
    Serial.print(steps2);
    Serial.println(" steps in the positive direction");
    
  }else{

    Serial.print("Stepper #2 needs to take ");
    Serial.print(abs(steps2));
    Serial.println(" steps in the negative direction");   
  }
}

void movemotor( int steps, String whichmotor){ //Moves motor by number of steps with delay, all given in parameters

  int count = 0; //Count variable to double check right number of loops
  String whichdirection;

  if( steps >= 0 ){ //Checks if steps are in positive direction

    digitalWrite( DIR_PIN1, LOW);
    digitalWrite( DIR_PIN2, LOW);
    digitalWrite( DIR_PIN3, LOW);
    whichdirection = "positive direction";
    
  }else{ //Else steps will be in negative direction

    digitalWrite( DIR_PIN1, HIGH);
    digitalWrite( DIR_PIN2, HIGH);
    digitalWrite( DIR_PIN3, HIGH);
    whichdirection = "negative direction";
  }

  steps = abs( steps );
  
  while( steps > 0 ){ //Loops for number of steps, stepping the motors, delayed by given delay (delay used so motors move simultaneously)

    if( whichmotor == "Stepper #1" ){ //Makes sure to step the correct pin
      digitalWrite(STEP_PIN1, HIGH);
      delayMicroseconds(100);
      digitalWrite(STEP_PIN1, LOW);
      delayMicroseconds(10);
      
    }else if( whichmotor == "Stepper #2" ){
      digitalWrite(STEP_PIN2, HIGH);
      delayMicroseconds(100);
      digitalWrite(STEP_PIN2, LOW);
      delayMicroseconds(100);
      
    }else if( whichmotor == "Stepper #3" ){
      digitalWrite(STEP_PIN3, HIGH);
      delayMicroseconds(100);
      digitalWrite(STEP_PIN3, LOW);
      delayMicroseconds(100);
    }
    count++;
    steps--;
  }

  Serial.print(whichmotor);
  Serial.print(" has taken "); //Confirm to user that the correct actions have been taken
  Serial.print(count);
  Serial.print(" steps in the ");
  Serial.println(whichdirection);
}

void followinstructions(){  

  Serial.print( "Current code is "); //Confirms to user that code is correct
  Serial.println(currentcode);
  int multiplier1 = 1;
  int multiplier2 = 1;
  int remainder1, remainder2;

  if( currentcode == 0 ){ //Checks for code G0

    movemotor( steps1, "Stepper #1"); //Moves motors as fast as possible directly to position
    movemotor( steps2, "Stepper #2");
    movemotor( steps3, "Stepper #3");
    
  }else if( currentcode == 1 ){ //Checks for code G1

    movemotor( steps3, "Stepper #3"); //Moves Z-axis first

    float realdesiredx = desiredx; //Saves actual desired values 
    float realdesiredy = desiredy;
    float slope = abs( ( (desiredy - currenty) / (desiredx - currentx) ) ); //Finds Slope

    int xmult = 1; //Declares multiplier values
    int ymult = 1;

    if( (desiredx - currentx) < 0 ){ //Changes multiplier values for if desired x or y is backwards 

      xmult = -1;
    }
    if( (desiredy - currenty) < 0 ){

      ymult = -1;
    }
    if( (desiredx - currentx) == 0 ){ //Checks for undefined slope

      slope = 1;
      xmult = 0;
    }

    //Loops while current values are not within range of real desired values
    while( !( ( ( currentx > (realdesiredx - .1) ) && ( currentx < (realdesiredx + .1) ) ) &&  ( ( currenty > (realdesiredy - .1) ) && ( currenty < (realdesiredy + .1) ) ) ) ){

      if( slope >= 1 ){ //Calculates intermediate values based on slope

        desiredy = currenty + (1 * ymult);
        desiredx = currentx + ( xmult * (1 / slope) );
       
      }else if( slope < 1 ){

        desiredy = currenty + (ymult * slope);
        desiredx = currentx + (1 * xmult);
      }

      cartesiantopolar(); //Calculates angles to get to intermediate points
      movemotor( steps1, "Stepper #1" ); //Moves motors accordingly
      movemotor( steps2, "Stepper #2" );

      currentangle1 = desiredangle1;
      currentangle2 = desiredangle2; //Updates the current angle settings
      currentx = desiredx; //Updates the current x and y 
      currenty = desiredy;

      //Prints comparison between current and desired values
      Serial.print( "Actual desired x: " );
      Serial.println( realdesiredx );
      Serial.print( "Actual desired y: " );
      Serial.println( realdesiredy );
      Serial.print( "Current x: " );
      Serial.println( currentx );
      Serial.print( "Current y: " );
      Serial.println( currenty );
    }

  }else if( currentcode == 20 ){ //Checks for code G20

    units = false; //Switches units to inches
    Serial.println( "User has switched input units to inches" );
    
  }else if( currentcode == 21){ //Checks for code G21

    units = true; //Switches units to mm
    Serial.println( "User has switched input units to mm" );
    
  }else if( currentcode == 90 ){

    absolutemode = true;
    Serial.println( "User has switched to absolute mode" );
    
  }else if( currentcode == 91 ){

    absolutemode = false;
    Serial.println( "User has switched to incremental mode" );
    
  }else if( currentcode == 02 ){

    repositiontoorigin();
    
  }else if( currentcode == 06 ){

    movemotor( 500, "Stepper #3" ); //Moves pen (5) steps (up?)

    Serial.println( "Waiting 5 seconds for pen/pencil change..." );
    delay(10000); //Delays 5 seconds to allow for pen change

    movemotor( -500, "Stepper #3" ); //Moves pen (-5) steps (down?)
  }
}

void repositiontoorigin(){ //Repositions to origin without drawing

  movemotor( 500, "Stepper #3" ); //Moves pen (5) steps (up?)

  desiredx = 0;
  desiredy = 0;
  desiredangle1 = 0; //Sets origin to be both angles at zero degrees
  desiredangle2 = 0;

  float angledifference1 = desiredangle1 - currentangle1; //Calculates the difference between desired angle and current angle (the amount of angle it needs to move)
  float angledifference2 = desiredangle2 - currentangle2;

  steps1 = 8.88 * angledifference1; //Calculates the amount of steps that each motor needs to move to achieve proper angle
  steps2 = 8.88 * angledifference2; //Assumes NEMA 17 motors with 200 steps/rev microstepped by 1/16 so 8.88 microsteps per degree

  movemotor( steps1, "Stepper #1"); //Moves motors as fast as possible directly to position
  movemotor( steps2, "Stepper #2");
  
  movemotor( -500, "Stepper #3" ); //Moves pen (-5) steps (down?)
}

void loop(){

  takeinstructions(); //Executes instruction function
}
