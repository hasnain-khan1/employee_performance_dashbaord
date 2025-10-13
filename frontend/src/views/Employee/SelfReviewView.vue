<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Self Review</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account-edit</v-icon>
            Current Review Cycle
          </v-card-title>
          <v-card-text>
            <div v-if="currentCycle">
              <h3>{{ currentCycle.name }}</h3>
              <p class="text-body-2">{{ currentCycle.description }}</p>
              <v-progress-linear
                :model-value="currentCycle.completion_percentage"
                color="primary"
                height="8"
                class="mt-2"
              />
              <div class="text-caption mt-1">
                {{ currentCycle.completion_percentage }}% Complete
              </div>
            </div>
            <div v-else>
              <p class="text-body-2">No active review cycle</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-clipboard-text</v-icon>
            Self Review Form
          </v-card-title>
          <v-card-text>
            <v-form ref="reviewForm" v-model="formValid">
              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Key Achievements</h3>
                  <v-textarea
                    v-model="reviewForm.achievements"
                    label="Describe your key achievements this period"
                    rows="4"
                    :rules="[v => !!v || 'Achievements are required']"
                    required
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Challenges Faced</h3>
                  <v-textarea
                    v-model="reviewForm.challenges"
                    label="Describe challenges you faced and how you addressed them"
                    rows="4"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Areas for Development</h3>
                  <v-textarea
                    v-model="reviewForm.development_areas"
                    label="What areas would you like to develop further?"
                    rows="4"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Goals for Next Period</h3>
                  <v-textarea
                    v-model="reviewForm.goals_for_next_period"
                    label="What are your goals for the next review period?"
                    rows="4"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Overall Self-Assessment</h3>
                  <v-rating
                    v-model="reviewForm.overall_rating"
                    color="yellow-darken-3"
                    size="large"
                    :rules="[v => !!v || 'Overall rating is required']"
                    required
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Additional Comments</h3>
                  <v-textarea
                    v-model="reviewForm.comments"
                    label="Any additional comments or feedback"
                    rows="3"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="grey"
              variant="text"
              @click="saveDraft"
            >
              Save Draft
            </v-btn>
            <v-btn
              color="primary"
              :disabled="!formValid"
              :loading="submitting"
              @click="submitReview"
            >
              Submit Review
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Reactive data
const reviewForm = ref({
  achievements: '',
  challenges: '',
  development_areas: '',
  goals_for_next_period: '',
  overall_rating: null,
  comments: ''
})

const formValid = ref(false)
const submitting = ref(false)
const currentCycle = ref({
  name: 'Q4 2024 Review Cycle',
  description: 'End of year performance review',
  completion_percentage: 65
})

// Methods
const saveDraft = async () => {
  try {
    // Save draft logic
    console.log('Saving draft:', reviewForm.value)
    toast.success('Draft saved successfully')
  } catch (error) {
    console.error('Error saving draft:', error)
    toast.error('Failed to save draft')
  }
}

const submitReview = async () => {
  try {
    submitting.value = true
    // Submit review logic
    console.log('Submitting review:', reviewForm.value)
    toast.success('Review submitted successfully')
  } catch (error) {
    console.error('Error submitting review:', error)
    toast.error('Failed to submit review')
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Load review data
  console.log('Self review loaded')
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>