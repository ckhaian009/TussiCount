# Biên dịch bộ chạy mô hình trên máy tính (Linux hoặc macOS). Dùng: make -f bien_dich.mk ...
# Thư viện Edge Impulse (giải nén từ tệp "C++ library" xuất ở Deployment) đặt trong EI_LIB,
# mặc định data/ei_lib/<ten_mo_hinh>, không đưa lên GitHub (giấy phép Edge Impulse).
#   make -f bien_dich.mk EI_LIB=../../data/ei_lib/v1
# Kết quả: build/<ten>/chay_mo_hinh

EI_LIB ?= ../../data/ei_lib/v1
TEN ?= $(notdir $(EI_LIB))
OUT := build/$(TEN)
CXX ?= g++
CC ?= gcc

CFLAGS := -O2 -DNDEBUG -DTF_LITE_DISABLE_X86_NEON=1 -DEIDSP_QUANTIZE_FILTERBANK=0 \
          -DEI_CLASSIFIER_ENABLE_DETECTION_POSTPROCESS_OP=1 -DEI_CLASSIFIER_USE_FULL_TFLITE=0 \
          -I$(EI_LIB) -I$(EI_LIB)/edge-impulse-sdk -I$(EI_LIB)/edge-impulse-sdk/third_party/flatbuffers/include \
          -I$(EI_LIB)/edge-impulse-sdk/third_party/gemmlowp -I$(EI_LIB)/edge-impulse-sdk/third_party/ruy \
          -Wno-unused-parameter
CXXFLAGS := $(CFLAGS) -std=c++17

SDK := $(EI_LIB)/edge-impulse-sdk
CXXSRC := $(wildcard $(EI_LIB)/tflite-model/*.cpp) \
          $(wildcard $(SDK)/dsp/kissfft/*.cpp) $(wildcard $(SDK)/dsp/dct/*.cpp) $(SDK)/dsp/memory.cpp \
          $(wildcard $(SDK)/porting/posix/*.cpp) \
          $(wildcard $(SDK)/tensorflow/lite/kernels/*.cc) $(wildcard $(SDK)/tensorflow/lite/kernels/internal/*.cc) \
          $(wildcard $(SDK)/tensorflow/lite/micro/kernels/*.cc) $(wildcard $(SDK)/tensorflow/lite/micro/*.cc) \
          $(wildcard $(SDK)/tensorflow/lite/micro/memory_planner/*.cc) \
          $(wildcard $(SDK)/tensorflow/lite/micro/arena_allocator/*.cc) \
          $(wildcard $(SDK)/tensorflow/lite/core/api/*.cc) $(wildcard $(SDK)/tensorflow/lite/schema/*.cc) \
          $(wildcard $(SDK)/tensorflow/lite/core/c/*.cc)
CSRC := $(wildcard $(SDK)/tensorflow/lite/c/*.c)
OBJ := $(patsubst $(EI_LIB)/%,$(OUT)/obj/%.o,$(CXXSRC) $(CSRC))

all: $(OUT)/chay_mo_hinh

$(OUT)/obj/%.cpp.o: $(EI_LIB)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@
$(OUT)/obj/%.cc.o: $(EI_LIB)/%.cc
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@
$(OUT)/obj/%.c.o: $(EI_LIB)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/chay_mo_hinh: chay_mo_hinh.cpp $(OBJ)
	@mkdir -p $(OUT)
	$(CXX) $(CXXFLAGS) chay_mo_hinh.cpp $(OBJ) -o $@ -lm

clean:
	rm -rf build

.PHONY: all clean
