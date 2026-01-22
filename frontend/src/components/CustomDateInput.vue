<template>
  <div class="relative">
    <!-- Custom styled wrapper -->
    <div class="relative w-full bg-white dark:bg-neutral-700 border border-gray-300 dark:border-neutral-600 rounded-lg shadow-sm hover:border-gray-400 dark:hover:border-neutral-500 transition-colors duration-200 focus-within:ring-2 focus-within:ring-slate-500 focus-within:border-slate-500">
      <input
        :value="modelValue"
        @input="handleInput"
        @change="handleChange"
        type="date"
        :min="minDate"
        :max="maxDate"
        :disabled="disabled"
        :required="required"
        class="w-full px-3 py-2.5 bg-transparent text-sm text-gray-900 dark:text-neutral-100 placeholder-gray-500 dark:placeholder-neutral-400 border-none outline-none focus:ring-0 disabled:opacity-50 disabled:cursor-not-allowed appearance-none"
        :class="{ 'cursor-not-allowed': disabled }"
      />
      
      <!-- Custom calendar icon -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="h-5 w-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CustomDateInput',
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
    minDate: {
      type: String,
      default: ''
    },
    maxDate: {
      type: String,
      default: ''
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
/* Hide native date picker icons in webkit browsers */
input[type="date"]::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  right: 0;
  width: 40px;
  height: 100%;
  cursor: pointer;
}

/* Hide native date picker icons in Firefox */
input[type="date"]::-moz-calendar-picker-indicator {
  opacity: 0;
}

/* Custom styling for the date input when focused */
input[type="date"]:focus {
  outline: none;
}
</style>