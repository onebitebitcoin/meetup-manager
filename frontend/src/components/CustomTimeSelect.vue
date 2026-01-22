<template>
  <div class="flex space-x-2">
    <!-- Hour Selection -->
    <div class="flex-1">
      <CustomSelect
        :model-value="selectedHour"
        :options="hourOptions"
        placeholder="시간"
        :required="required"
        @update:model-value="updateHour"
      />
    </div>
    
    <!-- Minute Selection -->
    <div class="flex-1">
      <CustomSelect
        :model-value="selectedMinute"
        :options="minuteOptions"
        placeholder="분"
        :required="required"
        @update:model-value="updateMinute"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import CustomSelect from './CustomSelect.vue'

export default {
  name: 'CustomTimeSelect',
  components: {
    CustomSelect,
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
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const selectedHour = ref('')
    const selectedMinute = ref('')

    // Generate hour options (00-23)
    const hourOptions = computed(() => {
      const hours = []
      for (let i = 0; i < 24; i++) {
        const hour = i.toString().padStart(2, '0')
        hours.push({ 
          value: hour, 
          label: `${hour}시`, 
        })
      }
      return hours
    })

    // Generate minute options (00, 15, 30, 45)
    const minuteOptions = computed(() => [
      { value: '00', label: '00분' },
      { value: '15', label: '15분' },
      { value: '30', label: '30분' },
      { value: '45', label: '45분' },
    ])

    // Parse initial value
    const parseTimeValue = (timeString) => {
      if (!timeString) return { hour: '', minute: '' }
      const [hour, minute] = timeString.split(':')
      return { 
        hour: hour || '', 
        minute: minute || '', 
      }
    }

    // Initialize from modelValue
    const initializeTime = () => {
      const { hour, minute } = parseTimeValue(props.modelValue)
      selectedHour.value = hour
      selectedMinute.value = minute
    }

    // Update functions
    const updateHour = (hour) => {
      selectedHour.value = hour
      emitTimeValue()
    }

    const updateMinute = (minute) => {
      selectedMinute.value = minute
      emitTimeValue()
    }

    const emitTimeValue = () => {
      if (selectedHour.value && selectedMinute.value) {
        const timeValue = `${selectedHour.value}:${selectedMinute.value}`
        emit('update:modelValue', timeValue)
        emit('change', timeValue)
      } else if (!selectedHour.value && !selectedMinute.value) {
        emit('update:modelValue', '')
        emit('change', '')
      }
    }

    // Watch for external changes to modelValue
    watch(() => props.modelValue, (newValue) => {
      const { hour, minute } = parseTimeValue(newValue)
      if (hour !== selectedHour.value || minute !== selectedMinute.value) {
        selectedHour.value = hour
        selectedMinute.value = minute
      }
    })

    // Initialize on mount
    initializeTime()

    return {
      selectedHour,
      selectedMinute,
      hourOptions,
      minuteOptions,
      updateHour,
      updateMinute,
    }
  },
}
</script>