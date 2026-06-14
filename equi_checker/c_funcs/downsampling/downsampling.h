#ifndef   DOWNSAMPLING_H
#define   DOWNSAMPLING_H

#include <stddef.h>

typedef struct {
    float sampling_rate;        // Abtastrate in Hz
    int   dsr;                  // DownSamplingRatio 
} SettingsDownSampling;

// Standardeinstellungen: 1000 Hz, DSR: 10
extern const SettingsDownSampling DefaultSettingsDownSampling;

/*
// Hilfsmakros: Ausgabegrößen
#define DS_OUT_SIZE_SIMPLE(in_size, dsr) ((in_size) / (size_t)(dsr))
#define DS_OUT_SIZE_CIC(in_size, dsr)    ((in_size) - 1 / (size_t)(dsr) + 1)
#define DS_OUT_SIZE_POLYPHASE(in_size)   ((in_size) / 2)
*/

// Hilfsfunktion: Berechnet Ausgangs-Abtastrate: SR_out = SR_in / dsr
float sampling_rate_out(const SettingsDownSampling *s);

// Downsampling-Algorithmen

// einfaches Downsampling: Mittelwert über dsr Samples
void do_simple(
        const SettingsDownSampling *s,
        const float *uin,
        size_t in_size,
        float *uout);
            
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

#endif /* DOWNSAMPLING_H */
