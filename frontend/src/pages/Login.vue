<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12" title="Вход">
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field v-model="email" label="Email" type="email" variant="outlined" />
              <v-text-field v-model="password" label="Пароль" type="password" variant="outlined" />
              <v-btn type="submit" color="primary" block class="mt-4">Войти</v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn variant="text" to="/register">Нет аккаунта? Регистрация</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>    
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router' // Импортируем хук роутера

const email = ref('')
const password = ref('')
const router = useRouter() // Инициализируем его

const handleLogin = async () => {
  try {
    // Вторым аргументом идет сам объект с данными (это пойдет в Body)
    const res = await axios.post('http://localhost:8000/login', {
      email: email.value,
      password: password.value
    });
    
    localStorage.setItem('user_id', res.data.user_id);
    router.push('/profile');
  } catch (e) {
    alert("Ошибка входа: " + (e.response?.data?.detail || "неверные данные"));
  }
}
</script>