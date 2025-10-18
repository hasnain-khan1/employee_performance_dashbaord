<template>
  <v-card variant="outlined" class="preview-section">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">{{ icon }}</v-icon>
      {{ title }}
      <v-spacer />
      <div class="d-flex align-center gap-2">
        <v-chip
          :color="isCompleted ? 'success' : 'warning'"
          variant="flat"
          size="small"
        >
          {{ isCompleted ? 'Completed' : 'In Progress' }}
        </v-chip>
        <v-chip
          color="primary"
          variant="outlined"
          size="small"
        >
          {{ wordCount }} words
        </v-chip>
      </div>
    </v-card-title>

    <v-card-text>
      <div class="preview-content">
        <div v-html="formattedContent" class="text-body-1"></div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  content: String,
  wordCount: Number,
  isCompleted: Boolean,
  icon: String
})

// Computed properties
const formattedContent = computed(() => {
  if (!props.content) return '<em>No content provided</em>'
  
  // Convert line breaks to HTML
  return props.content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[(.*?)\]/g, '<span class="reference">$1</span>')
})
</script>

<style scoped>
.preview-section {
  border-radius: 8px;
}

.preview-content {
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

.reference {
  background-color: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

.v-chip {
  font-weight: 500;
}
</style>
