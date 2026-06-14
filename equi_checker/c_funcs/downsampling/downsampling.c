#include "downsampling.h"

#include <math.h>
#include <stdlib.h>

// Standardeinstellung 
const SettingsDownSampling DefaultSettingsDownSampling = {
    .sampling_rate = 1000.0f,
    .dsr           = 10,
};

// Hilfsfunktion
float sampling_rate_out(const SettingsDownSampling *s)
{
    return s->sampling_rate / (float)s->dsr;
}

// Downsampling-Algorithmen

// einfaches Downsampling: Mittelwert über dsr Samples
void do_simple(
        const SettingsDownSampling *s,
        const float *uin,
        size_t in_size,
        float *uout)
{
    int    j,   
           dsr = s->dsr;
    size_t i,
           sz  = in_size / (size_t)dsr;
    float  sum;
    
    for (i = 0; i < sz; i++)
    {
        sum = 0.0f;
        for (j = 0; j < dsr; j++)
        {
            sum += uin[i * (size_t)dsr + (size_t)j];
        }
        uout[i] = sum / (float)dsr;
    }
}
            
/*
// CIC-Filter
void do_cic(
        const SettingsDownSampling *s,
        const float *uin, 
        size_t in_size,
        int num_stages,
        float *uout);

// FIR-Filter 1.Ordnung
void do_decimation_polyphase_order_one(
        const float *uin, 
        size_t in_size,
        float *uout);

// FIR-Filter 2.Ordnung
void do_decimation_polyphase_order_two(
        const float *uin, 
        size_t in_size,
        float *uout);

// mehrstufinger FIR-Filter 
// take_fist_order: 0 = zweite Ordnung, 1 = erste Ordnung
void do_decimation_polyphase(
        const SettingsDownSampling *s,
        const float *uin, 
        size_t in_size,
        int take_first_order,
        float *uout);
*/
