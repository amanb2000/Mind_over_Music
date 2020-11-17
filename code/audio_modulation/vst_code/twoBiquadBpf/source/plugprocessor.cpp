//------------------------------------------------------------------------
// Project     : VST SDK
//
// Category    : Examples
// Filename    : plugprocessor.cpp
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

#include "../include/plugprocessor.h"
#include "../include/plugids.h"

#include <cmath>
#include <math.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

#include "base/source/fstreamer.h"
#include "pluginterfaces/base/ibstream.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include "public.sdk/source/vst/vstaudioprocessoralgo.h"

namespace Steinberg {
namespace TwoBiquadBpf {

//-----------------------------------------------------------------------------
TwoBiquadBpfProcessor::TwoBiquadBpfProcessor ()
{
	// Init members
  mBypass = false;
  guiCtrlEnabled = false;

  //LPF
  lpfCutoffFreq = M_PI;
  lpfResonanceQFactor = MIN_RESONANCE_Q_FACTOR;
	lpfInputDelayBuf = NULL;
	lpfOutputDelayBuf = NULL;
	lpfFbFilterCoeffsA = NULL;
	lpfFfFilterCoeffsB = NULL;
	lpfAL = BIQUAD_NO_OF_FB_COEFFS;
	lpfBL = BIQUAD_NO_OF_FF_COEFFS;

  //HPF
  hpfCutoffFreq = 0;
  hpfResonanceQFactor = MIN_RESONANCE_Q_FACTOR;
  hpfInputDelayBuf = NULL;
  hpfOutputDelayBuf = NULL;
  hpfFbFilterCoeffsA = NULL;
  hpfFfFilterCoeffsB = NULL;
  hpfAL = BIQUAD_NO_OF_FB_COEFFS;
  hpfBL = BIQUAD_NO_OF_FF_COEFFS;

	// register its editor class
	setControllerClass (MyControllerUID);
}

//-----------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::initialize (FUnknown* context)
{
	//---always initialize the parent-------
	tresult result = AudioEffect::initialize (context);
	if (result != kResultTrue)
		return kResultFalse;

	//---create Audio In/Out buses------
	// we want a stereo Input and a Stereo Output
	addAudioInput (STR16 ("AudioInput"), Vst::SpeakerArr::kStereo);
	addAudioOutput (STR16 ("AudioOutput"), Vst::SpeakerArr::kStereo);

	return kResultTrue;
}

//-----------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::setBusArrangements (Vst::SpeakerArrangement* inputs,
                                                            int32 numIns,
                                                            Vst::SpeakerArrangement* outputs,
                                                            int32 numOuts)
{
	// we only support one in and output bus and these buses must have the same number of channels
	if (numIns == 1 && numOuts == 1 && inputs[0] == outputs[0])
	{
		return AudioEffect::setBusArrangements (inputs, numIns, outputs, numOuts);
	}
	return kResultFalse;
}

//-----------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::setupProcessing (Vst::ProcessSetup& setup)
{
	// here you get, with setup, information about:
	// sampleRate, processMode, maximum number of samples per audio block
	return AudioEffect::setupProcessing (setup);
}

//-----------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::setActive (TBool state)
{
	Vst::SpeakerArrangement arr;
	if (getBusArrangement(Vst::kOutput, 0, arr) != kResultTrue)
		return kResultFalse;
	int32 numChannels = Vst::SpeakerArr::getChannelCount(arr);

  //TODO: This should be size=MAX(AL,BL), currently mac 1sec duration
	size_t lpfDelayBufSize = processSetup.sampleRate * sizeof(Vst::Sample64) + 0.5;
  size_t hpfDelayBufSize = processSetup.sampleRate * sizeof(Vst::Sample64) + 0.5;

	if (state) // Initialize
	{
    //Initialize Delay Buffers for LPF and HPF
    lpfInputDelayBuf  = (double**) std::malloc(sizeof(double*) * numChannels);
		lpfOutputDelayBuf = (double**) std::malloc(sizeof(double*) * numChannels);
    hpfInputDelayBuf  = (double**) std::malloc(sizeof(double*) * numChannels);
    hpfOutputDelayBuf = (double**) std::malloc(sizeof(double*) * numChannels);
		for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
		{
			lpfInputDelayBuf[channelIdx]  = (double*) std::malloc(lpfDelayBufSize);
			lpfOutputDelayBuf[channelIdx] = (double*) std::malloc(lpfDelayBufSize);
			memset(lpfOutputDelayBuf[channelIdx], 0, lpfDelayBufSize);

      hpfInputDelayBuf[channelIdx]  = (double*) std::malloc(hpfDelayBufSize);
      hpfOutputDelayBuf[channelIdx] = (double*) std::malloc(hpfDelayBufSize);
      memset(lpfOutputDelayBuf[channelIdx], 0, hpfDelayBufSize);
		}

		//Initialize LPF as bypass
		lpfFbFilterCoeffsA = (double*) std::malloc(sizeof(double) * lpfBL);
		lpfFfFilterCoeffsB = (double*) std::malloc(sizeof(double) * lpfAL);
		memset(lpfFbFilterCoeffsA, 0, sizeof(double) * lpfBL);
		memset(lpfFfFilterCoeffsB, 0, sizeof(double) * lpfAL);
		lpfFfFilterCoeffsB[0] = 1; //Bypass x[n]
		lpfFbFilterCoeffsA[0] = 1; // a0 is always 1 in DSP theory

    //Initialize HPF as bypass
    hpfFbFilterCoeffsA = (double*) std::malloc(sizeof(double) * hpfBL);
    hpfFfFilterCoeffsB = (double*) std::malloc(sizeof(double) * hpfAL);
    memset(hpfFbFilterCoeffsA, 0, sizeof(double) * hpfBL);
    memset(hpfFfFilterCoeffsB, 0, sizeof(double) * hpfAL);
    hpfFfFilterCoeffsB[0] = 1; //Bypass x[n]
    hpfFbFilterCoeffsA[0] = 1; // a0 is always 1 in DSP theory
	}
	else // Release
	{
    //Free LPF Memory
		if (lpfOutputDelayBuf)
		{
			for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
			{
				std::free(lpfOutputDelayBuf[channelIdx]);
			}
			std::free(lpfOutputDelayBuf);
			lpfOutputDelayBuf = NULL;
		}
		if (lpfInputDelayBuf)
		{
			for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
			{
				std::free(lpfInputDelayBuf[channelIdx]);
			}
			std::free(lpfInputDelayBuf);
			lpfInputDelayBuf = NULL;
		}

		if (lpfFbFilterCoeffsA)
		{
			std::free(lpfFbFilterCoeffsA);
			lpfFbFilterCoeffsA = NULL;
		}
		if (lpfFfFilterCoeffsB)
		{
			std::free(lpfFfFilterCoeffsB);
			lpfFfFilterCoeffsB = NULL;
		}

    //Free HPF Memory
    if (hpfOutputDelayBuf)
    {
      for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
      {
        std::free(hpfOutputDelayBuf[channelIdx]);
      }
      std::free(hpfOutputDelayBuf);
      hpfOutputDelayBuf = NULL;
    }
    if (hpfInputDelayBuf)
    {
      for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
      {
        std::free(hpfInputDelayBuf[channelIdx]);
      }
      std::free(hpfInputDelayBuf);
      hpfInputDelayBuf = NULL;
    }

    if (hpfFbFilterCoeffsA)
    {
      std::free(hpfFbFilterCoeffsA);
      hpfFbFilterCoeffsA = NULL;
    }
    if (hpfFfFilterCoeffsB)
    {
      std::free(hpfFfFilterCoeffsB);
      hpfFfFilterCoeffsB = NULL;
    }

	}

	return AudioEffect::setActive (state);
}

//-----------------------------------------------------------------------------
template <typename Sample>
tresult TwoBiquadBpfProcessor::processAudio(Sample** in, Sample** out,
                                              int32 numSamples, int32 numChannels)
{
	for (int channelIdx = 0; channelIdx < numChannels; channelIdx++)
	{
    //System input/output buffers
		Sample* channelInputBuffer  = in[channelIdx];
		Sample* channelOutputBuffer = out[channelIdx];

		double* lpfChannelInputDelayBuffer  = lpfInputDelayBuf[channelIdx];
		double* lpfChannelOutputDelayBuffer = lpfOutputDelayBuf[channelIdx];
    double* hpfChannelInputDelayBuffer  = hpfInputDelayBuf[channelIdx];
    double* hpfChannelOutputDelayBuffer = hpfOutputDelayBuf[channelIdx];
		double x_n = 0; // Current Input  Sample
		double y_n = 0; // Current Output Sample

		//Filter Implementation
		for (int sampleIdx = 0; sampleIdx < numSamples; sampleIdx++)
		{
      //******************
      //LPF Implementation
      //******************
			x_n = channelInputBuffer[sampleIdx];
			y_n = 0;
			
			//Compute Output sample
			y_n = lpfFfFilterCoeffsB[0] * x_n +
              lpfFfFilterCoeffsB[1] * lpfChannelInputDelayBuffer[1] +
              lpfFfFilterCoeffsB[2] * lpfChannelInputDelayBuffer[2] -
              lpfFbFilterCoeffsA[1] * lpfChannelOutputDelayBuffer[1] -
              lpfFbFilterCoeffsA[2] * lpfChannelOutputDelayBuffer[2];
			
			//Update Delay Buffers
			lpfChannelInputDelayBuffer[2]  = lpfChannelInputDelayBuffer[1];
			lpfChannelInputDelayBuffer[1]  = x_n;
			lpfChannelOutputDelayBuffer[2] = lpfChannelOutputDelayBuffer[1];
			lpfChannelOutputDelayBuffer[1] = y_n;

      //******************
      //HPF Implementation
      //******************
      x_n = y_n; // Send LPF output to HPF input
      y_n = 0;

      //Compute Output sample
      y_n = hpfFfFilterCoeffsB[0] * x_n +
              hpfFfFilterCoeffsB[1] * hpfChannelInputDelayBuffer[1] +
              hpfFfFilterCoeffsB[2] * hpfChannelInputDelayBuffer[2] -
              hpfFbFilterCoeffsA[1] * hpfChannelOutputDelayBuffer[1] -
              hpfFbFilterCoeffsA[2] * hpfChannelOutputDelayBuffer[2];

      //Update Delay Buffers
      hpfChannelInputDelayBuffer[2]  = hpfChannelInputDelayBuffer[1];
      hpfChannelInputDelayBuffer[1]  = x_n;
      hpfChannelOutputDelayBuffer[2] = hpfChannelOutputDelayBuffer[1];
      hpfChannelOutputDelayBuffer[1] = y_n;

      //Send output sample of system to output buffer
			channelOutputBuffer[sampleIdx] = y_n;
		}
	}

	return kResultOk;
}


//-----------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::process (Vst::ProcessData& data)
{
	//--- Read inputs parameter changes-----------
  if (!guiCtrlEnabled)
  {
    //Read file
    std::ifstream inFile;
    std::string lineString;
    std::string varString;

    //Windows
    //inFile.open("C:/ProgramData/MOM/eegData.txt");

    //MacOS
    inFile.open("/Applications/MOM/audioModulationControl.txt");

    double controlParamSettings[NO_OF_CONTROL_PARAM_SETTINGS];

    if (!inFile) {
      exit(1);   // call system to stop
    }
    if (!inFile.eof()) // To get you all the lines.
    {
      getline(inFile, lineString); // Saves the line in STRING.
      std::stringstream ssin(lineString);
      int inputControlParamIdx = 0;
      while (ssin.good() && inputControlParamIdx < NO_OF_CONTROL_PARAM_SETTINGS) {
        ssin >> varString;
        // Normalize input params to 0-1 range
        controlParamSettings[inputControlParamIdx] =
          (double)std::stoi(varString) / MAX_CONTROL_PARAM_SETTING_VALUE;
        ++inputControlParamIdx;
      }
    }

    // Process Input data
    lpfCutoffFreq = 0.01 *
      pow(2.0, 8.295 * controlParamSettings[LPF_CUTOFF_CONTROL_SETTING_INDEX]);
    lpfResonanceQFactor = MIN_RESONANCE_Q_FACTOR +
      controlParamSettings[LPF_RESONANCE_CONTROL_SETTING_INDEX] *
      (MAX_RESONANCE_Q_FACTOR - MIN_RESONANCE_Q_FACTOR);
    hpfCutoffFreq = 0.01 *
      pow(2.0, 8.295 * controlParamSettings[HPF_CUTOFF_CONTROL_SETTING_INDEX]);
    hpfResonanceQFactor = MIN_RESONANCE_Q_FACTOR +
      controlParamSettings[HPF_RESONANCE_CONTROL_SETTING_INDEX] *
      (MAX_RESONANCE_Q_FACTOR - MIN_RESONANCE_Q_FACTOR);
  }

	if (data.inputParameterChanges)
	{
		int32 numParamsChanged = data.inputParameterChanges->getParameterCount ();
		for (int32 index = 0; index < numParamsChanged; index++)
		{
			Vst::IParamValueQueue* paramQueue =
        data.inputParameterChanges->getParameterData (index);
			if (paramQueue)
			{
				Vst::ParamValue value;
				int32 sampleOffset;
				int32 numPoints = paramQueue->getPointCount ();

				switch (paramQueue->getParameterId ())
				{
          case TwoBiquadBpfParams::kGuiCtrlId:
          if (paramQueue->getPoint(numPoints - 1, sampleOffset, value) ==
              kResultTrue)
            // Enable Manual Control from GUI in host
            guiCtrlEnabled = value;
          break;
					case TwoBiquadBpfParams::kLpfCutoffFreqId:
						if (guiCtrlEnabled &&
                paramQueue->getPoint(numPoints - 1, sampleOffset, value) ==
							  kResultTrue)
              // Convert linear 0-1 input to exponential (base 2) 0.01-PI cutoff
							lpfCutoffFreq = 0.01 * pow(2.0, 8.295 * value);
						break;
					case TwoBiquadBpfParams::kLpfResonanceQId://resonatorQ
						if (guiCtrlEnabled &&
                paramQueue->getPoint(numPoints - 1, sampleOffset, value) ==
							  kResultTrue)
							lpfResonanceQFactor =MIN_RESONANCE_Q_FACTOR +
                value * (MAX_RESONANCE_Q_FACTOR - MIN_RESONANCE_Q_FACTOR);
						break;
          case TwoBiquadBpfParams::kHpfCutoffFreqId:
            if (guiCtrlEnabled &&
                paramQueue->getPoint(numPoints - 1, sampleOffset, value) ==
                kResultTrue)
              // Convert linear 0-1 input to exponential (base 2) 0.01-PI cutoff
              hpfCutoffFreq = 0.01 * pow(2.0, 8.295 * value);
            break;
          case TwoBiquadBpfParams::kHpfResonanceQId://resonatorQ
            if (guiCtrlEnabled &&
                paramQueue->getPoint(numPoints - 1, sampleOffset, value) ==
                kResultTrue)
              hpfResonanceQFactor = MIN_RESONANCE_Q_FACTOR +
                value * (MAX_RESONANCE_Q_FACTOR - MIN_RESONANCE_Q_FACTOR);
            break;
					case TwoBiquadBpfParams::kBypassId:
						if (paramQueue->getPoint (numPoints - 1, sampleOffset, value) ==
						    kResultTrue)
							mBypass = (value > 0.5f);
						break;
				}
			}
		}
  }

  //LPF Coefficient parameter calculation
  double beta = 0.5 * (1.0 - sin(lpfCutoffFreq) / (2.0 * lpfResonanceQFactor)) /
                  (1.0 + sin(lpfCutoffFreq) / (2.0 * lpfResonanceQFactor));
  double gamma = (0.5 + beta) * cos(lpfCutoffFreq);

  //Feedback Coefficients (A)
  lpfFbFilterCoeffsA[1] = -2.0 * gamma;
  lpfFbFilterCoeffsA[2] = 2.0 * beta;

  //Feed-forward Coefficients (B)
  lpfFfFilterCoeffsB[0] = (0.5 + beta - gamma) / 2.0;
  lpfFfFilterCoeffsB[1] = 0.5 + beta - gamma;
  lpfFfFilterCoeffsB[2] = lpfFfFilterCoeffsB[0];

  //HPF Coefficient parameter calculation
  beta = 0.5 * (1.0 - sin(hpfCutoffFreq) / (2.0 * hpfResonanceQFactor)) /
           (1.0 + sin(hpfCutoffFreq) / (2.0 * hpfResonanceQFactor));
  gamma = (0.5 + beta) * cos(hpfCutoffFreq);

  //Feedback Coefficients (A)
  hpfFbFilterCoeffsA[1] = -2.0 * gamma;
  hpfFbFilterCoeffsA[2] = 2.0 * beta;

  //Feed-forward Coefficients (B)
  hpfFfFilterCoeffsB[0] = (0.5 + beta + gamma) / 2.0;
  hpfFfFilterCoeffsB[1] = -1.0 * (0.5 + beta + gamma);
  hpfFfFilterCoeffsB[2] = hpfFfFilterCoeffsB[0];

	//--- Process Audio---------------------
	//--- ----------------------------------
	if (data.numInputs == 0 || data.numOutputs == 0)
	{
		// nothing to do
		return kResultOk;
	}

	if (data.numSamples > 0)
	{
		// Process Algorithm
		void** in = getChannelBuffersPointer(processSetup, data.inputs[0]);
		void** out = getChannelBuffersPointer(processSetup, data.outputs[0]);

		if (Vst::kSample32 == processSetup.symbolicSampleSize)
		{
			processAudio<Vst::Sample32>((Vst::Sample32**)in, (Vst::Sample32**)out,
                                  data.numSamples, data.inputs[0].numChannels);
		}
		else
		{
			processAudio<Vst::Sample64>((Vst::Sample64**)in, (Vst::Sample64**)out,
                                  data.numSamples, data.inputs[0].numChannels);
		}
	}
	return kResultOk;
}

//------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::setState (IBStream* state)
{
	if (!state)
		return kResultFalse;

	// called when we load a preset or project, the model has to be reloaded

	IBStreamer streamer (state, kLittleEndian);

	float savedParam1 = 0.f;
	if (streamer.readFloat (savedParam1) == false)
		return kResultFalse;

	int32 savedParam2 = 0;
	if (streamer.readInt32 (savedParam2) == false)
		return kResultFalse;

	int32 savedBypass = 0;
	if (streamer.readInt32 (savedBypass) == false)
		return kResultFalse;

	mBypass = savedBypass > 0;

	return kResultOk;
}

//------------------------------------------------------------------------
tresult PLUGIN_API TwoBiquadBpfProcessor::getState (IBStream* state)
{
	// here we need to save the model (preset or project)

	float toSaveParam1 = 0;
	int32 toSaveParam2 = 0;
	int32 toSaveBypass = mBypass ? 1 : 0;

	IBStreamer streamer (state, kLittleEndian);
	streamer.writeFloat (toSaveParam1);
	streamer.writeInt32 (toSaveParam2);
	streamer.writeInt32 (toSaveBypass);

	return kResultOk;
}

//------------------------------------------------------------------------
} // namespace
} // namespace Steinberg
