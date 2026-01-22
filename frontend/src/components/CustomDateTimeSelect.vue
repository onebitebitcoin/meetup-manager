<template>
  <div class="space-y-3">
    <!-- Date Selection -->
    <div>
      <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">날짜</label>
      <CustomDateInput
        :model-value="selectedDate"
        :min-date="minDate"
        :max-date="maxDate"
        :required="required"
        :disabled="disabled"
        @update:model-value="updateDate"
      />
    </div>
    
    <!-- Time Selection -->
    <div>
      <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">시간</label>
      <CustomTimeSelect
        :model-value="selectedTime"
        :required="required"
        :disabled="disabled"
        @update:model-value="updateTime"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import CustomDateInput from './CustomDateInput.vue'
import CustomTimeSelect from './CustomTimeSelect.vue'

export default {
  name: 'CustomDateTimeSelect',
  components: {
    CustomDateInput,
    CustomTimeSelect,
  },
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    required: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    minDateTime: {
      type: String,
      default: '',
    },
    maxDateTime: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const selectedDate = ref('')
    const selectedTime = ref('')

    // Compute min/max dates from datetime props
    const minDate = computed(() => {
      if (!props.minDateTime) return ''
      return props.minDateTime.split('T')[0]
    })

    const maxDate = computed(() => {
      if (!props.maxDateTime) return ''
      return props.maxDateTime.split('T')[0]
    })

    // Parse datetime value
    const parseDateTimeValue = (dateTimeString) => {
      if (!dateTimeString) return { date: '', time: '' }
      
      // Handle both ISO format and local datetime format
      let dateTime
      if (dateTimeString.includes('T')) {
        dateTime = new Date(dateTimeString)
      } else {
        dateTime = new Date(dateTimeString)
      }
      
      if (isNaN(dateTime.getTime())) {
        return { date: '', time: '' }
      }

      const date = dateTime.toISOString().split('T')[0]
      const hours = dateTime.getHours().toString().padStart(2, '0')
      const minutes = dateTime.getMinutes().toString().padStart(2, '0')
      const time = `${hours}:${minutes}`

      return { date, time }
    }

    // Initialize from modelValue
    const initializeDateTime = () => {
      const { date, time } = parseDateTimeValue(props.modelValue)
      selectedDate.value = date
      selectedTime.value = time
    }

    // Update functions
    const updateDate = (date) => {
      selectedDate.value = date
      emitDateTimeValue()
    }

    const updateTime = (time) => {
      selectedTime.value = time
      emitDateTimeValue()
    }

    const emitDateTimeValue = () => {
      if (selectedDate.value && selectedTime.value) {
        // Create datetime-local format for form compatibility
        const dateTimeValue = `${selectedDate.value}T${selectedTime.value}`
        emit('update:modelValue', dateTimeValue)
        emit('change', dateTimeValue)
      } else if (!selectedDate.value && !selectedTime.value) {
        emit('update:modelValue', '')
        emit('change', '')
      }
    }

    // Watch for external changes to modelValue
    watch(() => props.modelValue, (newValue) => {
      const { date, time } = parseDateTimeValue(newValue)
      if (date !== selectedDate.value || time !== selectedTime.value) {
        selectedDate.value = date
        selectedTime.value = time
      }
    })

    // Initialize on mount
    initializeDateTime()

    return {
      selectedDate,
      selectedTime,
      minDate,
      maxDate,
      updateDate,
      updateTime,
    }
  },
}
</script>