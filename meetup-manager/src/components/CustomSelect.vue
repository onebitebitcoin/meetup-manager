<template>
  <div class="relative">
    <!-- Hidden native select for form compatibility -->
    <select
      v-model="selectedValue"
      @change="handleChange"
      class="sr-only"
      :disabled="disabled"
    >
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>

    <!-- Custom styled button -->
    <button
      type="button"
      @click="toggleDropdown"
      @blur="handleBlur"
      :disabled="disabled"
      class="relative w-full bg-white dark:bg-neutral-700 border border-gray-300 dark:border-neutral-600 rounded-lg shadow-sm pl-3 pr-10 py-2.5 text-left cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-colors duration-200 hover:border-gray-400 dark:hover:border-neutral-500 disabled:opacity-50 disabled:cursor-not-allowed"
      :class="{
        'ring-2 ring-slate-500 border-slate-500': isOpen
      }"
    >
      <span class="block truncate text-sm text-gray-900 dark:text-neutral-100">
        {{ selectedOption?.label || placeholder }}
      </span>
      <span class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
        <svg
          class="h-5 w-5 text-neutral-400 transition-transform duration-200"
          :class="{ 'rotate-180': isOpen }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </span>
    </button>

    <!-- Dropdown menu -->
    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-full bg-white dark:bg-neutral-700 shadow-lg max-h-60 rounded-lg py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none border border-gray-200 dark:border-neutral-600"
      >
        <div
          v-for="option in options"
          :key="option.value"
          @click="selectOption(option)"
          class="cursor-pointer select-none relative py-2.5 pl-3 pr-9 hover:bg-gray-50 dark:hover:bg-neutral-600 transition-colors duration-150"
          :class="{
            'bg-slate-100 dark:bg-neutral-600 text-slate-900 dark:text-neutral-100': option.value === selectedValue,
            'text-gray-900 dark:text-neutral-100': option.value !== selectedValue
          }"
        >
          <span
            class="block truncate text-sm"
            :class="{
              'font-medium': option.value === selectedValue,
              'font-normal': option.value !== selectedValue
            }"
          >
            {{ option.label }}
          </span>

          <!-- Checkmark for selected option -->
          <span
            v-if="option.value === selectedValue"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-600 dark:text-neutral-300"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'CustomSelect',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    options: {
      type: Array,
      required: true,
      default: () => []
    },
    placeholder: {
      type: String,
      default: 'Select an option'
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const isOpen = ref(false)
    const selectedValue = ref(props.modelValue)

    const selectedOption = computed(() => {
      return props.options.find(option => option.value === selectedValue.value)
    })

    const toggleDropdown = () => {
      if (!props.disabled) {
        isOpen.value = !isOpen.value
      }
    }

    const selectOption = (option) => {
      selectedValue.value = option.value
      emit('update:modelValue', option.value)
      emit('change', option.value)
      isOpen.value = false
    }

    const handleChange = () => {
      emit('update:modelValue', selectedValue.value)
      emit('change', selectedValue.value)
    }

    const handleBlur = (event) => {
      // Small delay to allow click events to register
      setTimeout(() => {
        if (!event.currentTarget.contains(document.activeElement)) {
          isOpen.value = false
        }
      }, 100)
    }

    const handleClickOutside = (event) => {
      const element = event.target.closest('.relative')
      if (!element || !element.contains(event.target)) {
        isOpen.value = false
      }
    }

    const handleKeydown = (event) => {
      if (event.key === 'Escape') {
        isOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleKeydown)
    })

    // Watch for external changes to modelValue
    const updateSelectedValue = (newValue) => {
      selectedValue.value = newValue
    }

    // Update when prop changes
    const unwatchModelValue = () => {
      if (props.modelValue !== selectedValue.value) {
        selectedValue.value = props.modelValue
      }
    }

    return {
      isOpen,
      selectedValue,
      selectedOption,
      toggleDropdown,
      selectOption,
      handleChange,
      handleBlur,
      unwatchModelValue
    }
  },
  watch: {
    modelValue(newValue) {
      this.selectedValue = newValue
    }
  }
}
</script>