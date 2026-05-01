<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12" rounded="lg">
          <v-toolbar color="primary" title="Регистрация"></v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="email"
                label="Email"
                prepend-inner-icon="mdi-email-outline"
                variant="outlined"
                type="email"
              />
              <v-text-field
                v-model="password"
                label="Пароль"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
                type="password"
              />
              <v-text-field
                v-model="passwordConfirm"
                label="Подтвердите пароль"
                prepend-inner-icon="mdi-lock-check-outline"
                variant="outlined"
                type="password"
              />
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                class="mt-4"
                :loading="loading"
              >
                Зарегистрироваться
              </v-btn>
            </v-form>
            
            <v-alert v-if="success" type="success" variant="tonal" class="mt-4">
              Письмо с ключом отправлено на почту
            </v-alert>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn variant="text" to="/login">Уже есть аккаунт? Войти</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import axios from 'axios'

const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)
const success = ref(false)

const handleRegister = async () => {
  loading.value = true
  try {
    // Убедись, что твой FastAPI запущен на 8000 порту
    await axios.post('http://localhost:8000/register', {
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value
    })
    success.value = true
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Ошибка регистрации')
  } finally {
    loading.value = false
  }
}
</script>