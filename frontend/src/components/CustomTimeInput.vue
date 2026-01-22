<template>
  <div class="relative">
    <!-- Custom styled wrapper -->
    <div class="relative w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:border-gray-400 dark:hover:border-gray-500 transition-colors duration-200 focus-within:ring-2 focus-within:ring-slate-500 focus-within:border-slate-500">
      <input
        :value="modelValue"
        @input="handleInput"
        @change="handleChange"
        type="time"
        :disabled="disabled"
        :required="required"
        :step="step"
        class="w-full px-3 py-2.5 pr-10 bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 border-none outline-none focus:ring-0 disabled:opacity-50 disabled:cursor-not-allowed"
        :class="{ 'cursor-not-allowed': disabled }"
      />
      
      <!-- Custom clock icon -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CustomTimeInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    step: {
      type: [String, Number],
      default: 60
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const handleInput = (event) => {
      emit('update:modelValue', event.target.value)
    }

    const handleChange = (event) => {
      emit('change', event.target.value)
    }

    return {
      handleInput,
      handleChange
    }
  }
}
</script>

<style scoped>
/* Hide native time picker icons in webkit browsers while maintaining functionality */
input[type="time"]::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  right: 0;
  width: 40px;
  height: 100%;
  cursor: pointer;
  z-index: 10;
}

/* Safari specific fixes */
input[type="time"] {
  position: relative;
  z-index: 1;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

/* Hide native time picker icons in Firefox */
input[type="time"]::-moz-calendar-picker-indicator {
  opacity: 0;
}

/* Custom styling for the time input when focused */
input[type="time"]:focus {
  outline: none;
}

/* Ensure the custom icon doesn't interfere with click area */
.absolute.inset-y-0.right-0 {
  z-index: 5;
  pointer-events: none;
}
</style>