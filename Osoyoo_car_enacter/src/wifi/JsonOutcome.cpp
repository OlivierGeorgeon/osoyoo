#include "JsonOutcome.h"
#include "Arduino_JSON.h"

JsonOutcome::JsonOutcome()
{
    data = JSON.parse("{}");
}

void JsonOutcome::addValue(char key[], String value)
{
    data[(String) key] = value;
}

String JsonOutcome::get()
{
    return JSON.stringify(data);
}

void JsonOutcome::clear()
{
    data = JSON.parse("{}");
}