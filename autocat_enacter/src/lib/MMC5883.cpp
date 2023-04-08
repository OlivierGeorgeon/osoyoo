#include "MMC5883.h"
#include <Arduino.h>
#include <math.h>
#include <Wire.h>


MMC5883MA::MMC5883MA(){
  wire = &Wire;
}

void MMC5883MA::begin()
{
    // Olivier: Avoids freezing the main loop
    wire->setWireTimeout( 25000, true);

    wire->beginTransmission(MMC_ADDRESS);
    // the address of the register is written first
    // in this case CONTROL REGISTER 0
    wire->write(COMPASS_CONFIG_REGISTER);
    // then the data is written. I nthis case a 1 in the 4th position or hex 0x8
    wire->write(COMPASS_CONFIG_REGISTER);
    // end transmission sents a STOP to indicate the end of the WRITE
    wire->endTransmission();

    // now as a verification read the device ID

    wire->beginTransmission(MMC_ADDRESS);
    // write a 2f to the register to read
    wire->write(Product_ID);
    // send a STOP WRITE
    wire->endTransmission();
    // this tells the chip to send 1 byte from that register
    // in i2c this is a START READ
    wire->requestFrom(MMC_ADDRESS, 1);
    // we then wait for 1 byte to be recieved
    while (wire->available() < 1)
        ;
    // once the byte arrives we read it.
    ID = wire->read();
    //send another STOP READ
    wire->endTransmission();
    // print out the ID which is 0x0C
    Serial.print("ID = ");
    Serial.println(ID);
}

void MMC5883MA::calibrate()
{
    static int count = 0;
    Serial.println("Please wait until calibration is done!");
    while (count < 10000)
    {
        wire->beginTransmission(MMC_ADDRESS);
        wire->write(COMPASS_CONFIG_REGISTER);
        wire->write(1);
        wire->endTransmission();
        // we have to continually read the status register and look for bit zero to go TRUE
        while ((reg & 1) == 0)
        {
            // write the register 0x7
            wire->beginTransmission(MMC_ADDRESS);
            wire->write(COMPASS_STATUS_REGISTER);
            wire->endTransmission();
            // read 1 byte
            wire->requestFrom(MMC_ADDRESS, 1);
            while (wire->available() < 1)
                ;
            reg = wire->read();
            wire->endTransmission();
            // let the WHILE evaluate the results once a TRUE condition is detected we continue on
        }
        // set the read register to 0
        wire->beginTransmission(MMC_ADDRESS);
        wire->write(COMPASS_DATA_REGISTER);
        wire->endTransmission();
        // request 6 values
        wire->requestFrom(MMC_ADDRESS, 6);
        // wait until 6 are recieved
        while (wire->available() < 6)
            ;
        // read the six values
        // I used shot int to prevent negative number
        // they all need to be positive
        xLSB = wire->read();
        xMSB = wire->read();
        yLSB = wire->read();
        yMSB = wire->read();
        zLSB = wire->read();
        zMSB = wire->read();

        wire->endTransmission();
        // shifting a byte left 8 spaces multiplys it by 256 to move it to the
        // upper byte position in a word. Adding the lsb gives the true number
        // I used long here to prevent any negatives
        sx = (long)(xMSB << 8) + xLSB;
        sy = (long)(yMSB << 8) + yLSB;
        sz = (long)(zMSB << 8) + zLSB;
        // on the first pass I just capture the initial values
        if (count == 0)
        {
            xMax = xMin = sx;
            yMax = yMin = sy;
            zMax = zMin = sz;
        }
        // then I determine if it is a max or a min or neither
        if (xMax < sx)
            xMax = sx;
        if (xMin > sx)
            xMin = sx;
        if (yMax < sy)
            yMax = sy;
        if (yMin > sy)
            yMin = sy;
        if (zMax < sz)
            zMax = sz;
        if (zMin > sz)
            zMin = sz;
        /*Serial.print("X = ");
    Serial.print(sx) ; 
    Serial.print(" Y = ");
    Serial.print(sy); 
    Serial.print(" Z = ");
    Serial.println(sz);*/
        /*delay(100);*/
        // just a little debug so I can see how long to go
        // using the mod operator it limits the output to 10 lines 0 through 9000
        if ((count % 1000) == 0)
            Serial.print(".");
        count++;
    }
    Serial.println(".");
}

void MMC5883MA::update()
{
    reg = 0;
    wire->beginTransmission(MMC_ADDRESS);
    wire->write(COMPASS_CONFIG_REGISTER);
    wire->write(1);
    wire->endTransmission();
    while ((reg & 1) == 0)
    {
        wire->beginTransmission(MMC_ADDRESS);
        wire->write(COMPASS_STATUS_REGISTER);
        wire->endTransmission();
        wire->requestFrom(MMC_ADDRESS, 1);
        while (wire->available() < 1)
            ;
        reg = wire->read();
        wire->endTransmission();
    }
    wire->beginTransmission(MMC_ADDRESS);
    wire->write(COMPASS_DATA_REGISTER);
    wire->endTransmission();
    wire->requestFrom(MMC_ADDRESS, 6);
    while (wire->available() < 6)
        ;
    xLSB = wire->read();
    xMSB = wire->read();
    yLSB = wire->read();
    yMSB = wire->read();
    zLSB = wire->read();
    zMSB = wire->read();

    wire->endTransmission();
    sx = (long)(xMSB << 8) + xLSB;
    sy = (long)(yMSB << 8) + yLSB;
    sz = (long)(zMSB << 8) + zLSB;

    //***************************************************************************
    //  Evaluation time.
    //***************************************************************************
    // this read convert the data from garbage to a value from -1.0 to +1.0
    // this says subrtact the min from the value to shift it to a number starting at zero
    // subtract the min from the max to create a range
    // devide the shifted number by that range to give a percent from xero to one
    // multiply by 2 and subtract 1 giving a number -1.0 to +1.0
    // the reason this works is simple...
    // for the x axis when it is pointed north it is at its minimal value
    // when it is pointed north it is at its max so north is zero south is -1.0
    // from x only you can't tell east or west
    // y is 1.0 pointing west and -1.0 pointing east
    // z is one pointed at the center of the earth and -1 pointing away
    // these three combined have converted the values to a UNIT SPhere or a sphere with
    // radius of one.

    x = 2.0 * (float)(sx - xMin) / (float)(xMax - xMin) - 1.0;
    y = 2.0 * (float)(sy - yMin) / (float)(yMax - yMin) - 1.0;
    z = 2.0 * (float)(sz - zMin) / (float)(zMax - zMin) - 1.0;
}

float MMC5883MA::getX()
{
    return x;
}

float MMC5883MA::getY()
{
    return y;
}

float MMC5883MA::getZ()
{
    return z;
}

float MMC5883MA::getAngel()
{
    // now that we have x any in units we need for trigonometry
    // we can create a compass
    // if you are wanting to make a compass with the chip parallel to the ground
    // you only have to spin it in the x-y plane z doesnt matter.
    // when you know the opposite Y and the adjacent X you use arctangent to ge the angle

    // arc tangen is only good for one half the circle. It repeats itself in the other half.
    // the function is mirrored on the diagonal (math talk)
    // arctangent is not valid with x = 0.0

    if (x != 0.0)
    {
        // if x is positive the we use ther returned angle and convert it to degrees
        // it is faster just to mutiply with 100/PI already evaluated
        if (x > 0.0)
            angle = 57.2958 * atan(y / x);

        // if x is less than 0.0 we have to determine which quardant by looking at Y
        if (x < 0.0)
        {
            // y below zero subtract 180 from the answer
            if (y < 0.0)
                angle = 57.2958 * atan(y / x) - 180.0;
            // y > 0.0 add 180
            if (y > 0.0)
                angle = 57.2958 * atan(y / x) + 180.0;
        }
    }
    return angle;
}

String MMC5883MA::readData()
{
    update();
    String value = "Mag X:";
    value += x;
    value += "\tY:";
    value += y;
    value += "  \tZ:";
    value += z;
    return value;
}

// Olivier Georgeon for compatibility with HMC5883
void MMC5883MA::setOffset(int xo, int yo)
{
    xOffset = xo;
    yOffset = yo;
}

// Olivier Georgeon for compatibility with HMC5883
Vector MMC5883MA::readNormalize(void)
{
    update();
    v.XAxis = (float)sx/5.0 - xOffset;
    v.YAxis = (float)sy/5.0 - yOffset;
    v.ZAxis = (float)sy;
    return v;
}
