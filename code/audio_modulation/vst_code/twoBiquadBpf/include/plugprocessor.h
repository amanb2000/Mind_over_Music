//------------------------------------------------------------------------
// Project     : VST SDK
//
// Category    : Examples
// Filename    : plugprocessor.h
// Created by  : Steinberg, 01/2018
// Description : HelloWorld Example for VST 3
//
//-----------------------------------------------------------------------------
// LICENSE
// (c) 2019, Steinberg Media Technologies GmbH, All Rights Reserved
//-----------------------------------------------------------------------------
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
// 
//   * Redistributions of source code must retain the above copyright notice, 
//     this list of conditions and the following disclaimer.
//   * Redistributions in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation 
//     and/or other materials provided with the distribution.
//   * Neither the name of the Steinberg Media Technologies nor the names of its
//     contributors may be used to endorse or promote products derived from this 
//     software without specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
// IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
// INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
// BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
// OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
// OF THE POSSIBILITY OF SUCH DAMAGE.
//-----------------------------------------------------------------------------

#pragma once

#include "public.sdk/source/vst/vstaudioeffect.h"


namespace Steinberg {
namespace TwoBiquadBpf {

#define _USE_MATH_DEFINES
#define BIQUAD_NO_OF_FB_COEFFS 3
#define BIQUAD_NO_OF_FF_COEFFS 3
#define MIN_RESONANCE_Q_FACTOR 0.707
#define MAX_RESONANCE_Q_FACTOR 40.0
#define MAX_CONTROL_PARAM_SETTING_VALUE 1000.0

//-----------------------------------------------------------------------------
class TwoBiquadBpfProcessor : public Vst::AudioEffect
{
public:
	TwoBiquadBpfProcessor ();

	tresult PLUGIN_API initialize (FUnknown* context) SMTG_OVERRIDE;
	tresult PLUGIN_API setBusArrangements (Vst::SpeakerArrangement* inputs, int32 numIns,
	                                       Vst::SpeakerArrangement* outputs, int32 numOuts) SMTG_OVERRIDE;

	tresult PLUGIN_API setupProcessing (Vst::ProcessSetup& setup) SMTG_OVERRIDE;
	tresult PLUGIN_API setActive (TBool state) SMTG_OVERRIDE;
	tresult PLUGIN_API process (Vst::ProcessData& data) SMTG_OVERRIDE;

//------------------------------------------------------------------------
	tresult PLUGIN_API setState (IBStream* state) SMTG_OVERRIDE;
	tresult PLUGIN_API getState (IBStream* state) SMTG_OVERRIDE;

	static FUnknown* createInstance (void*)
	{
		return (Vst::IAudioProcessor*)new TwoBiquadBpfProcessor ();
	}

protected:
	template <typename Sample>
	tresult processAudio(Sample** in, Sample** out, int32 numSamples, int32 numChannels);

  bool mBypass;
  bool guiCtrlEnabled;

  //Low-Pass Filter (LPF)
  double lpfCutoffFreq;
  double lpfResonanceQFactor;
	double* lpfFbFilterCoeffsA;
	double* lpfFfFilterCoeffsB;
	int32 lpfBL;
	int32 lpfAL;
  double** lpfInputDelayBuf; // [channel][sample]
  double** lpfOutputDelayBuf;

  //High-Pass Filter (HPF)
  double hpfCutoffFreq;
  double hpfResonanceQFactor;
  double* hpfFbFilterCoeffsA;
  double* hpfFfFilterCoeffsB;
  int32 hpfBL;
  int32 hpfAL;
  double** hpfInputDelayBuf; // [channel][sample]
  double** hpfOutputDelayBuf;
};

enum ControlParamSettingIndex
{
  HPF_CUTOFF_CONTROL_SETTING_INDEX,
  HPF_RESONANCE_CONTROL_SETTING_INDEX,
  LPF_CUTOFF_CONTROL_SETTING_INDEX,
  LPF_RESONANCE_CONTROL_SETTING_INDEX,
  NO_OF_CONTROL_PARAM_SETTINGS
};

//------------------------------------------------------------------------
} // namespace
} // namespace Steinberg
