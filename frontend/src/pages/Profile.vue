<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card class="elevation-12" rounded="lg">
          <v-toolbar color="primary" title="Личный кабинет"></v-toolbar>
          
          <v-card-text>
            <div class="mb-6">
              <div class="text-subtitle-1 mb-2">Ваш текущий ключ активации:</div>
              <v-chip
                color="primary"
                variant="outlined"
                size="large"
                class="font-weight-bold"
              >
                {{ activationKey }}
              </v-chip>
              <v-btn 
                color="secondary" 
                class="ml-4" 
                @click="refreshKey" 
                :loading="updatingKey"
              >
                Обновить ключ
              </v-btn>
            </div>

            <v-divider class="my-4"></v-divider>

            <div class="text-h6 mb-4">Смена пароля</div>
            <v-form @submit.prevent="changePassword">
              <v-text-field v-model="passwords.old" label="Старый пароль" type="password" variant="outlined" />
              <v-text-field v-model="passwords.new" label="Новый пароль" type="password" variant="outlined" />
              <v-text-field v-model="passwords.confirm" label="Подтвердите пароль" type="password" variant="outlined" />
              <v-btn type="submit" color="primary" block>Сохранить новый пароль</v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" variant="text" @click="logout">Выйти</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const userId = localStorage.getItem('user_id')

// Реактивные переменные
const activationKey = ref('Загрузка...')
const updatingKey = ref(false)
const passwords = ref({ old: '', new: '', confirm: '' }) // Добавил confirm для бэкенда

// 1. Загрузка ключа (GET /getkey)
const fetchKey = async () => {
  if (!userId) return
  try {
    const res = await axios.get(`http://localhost:8000/getkey`, {
      params: { user_id: userId }
    })
    // Если ключа в базе нет (null), оставим заглушку
    activationKey.value = res.data || 'Ключ еще не сгенерирован'
  } catch (e) {
    console.error("Ошибка при получении ключа:", e)
    activationKey.value = 'Ошибка загрузки'
  }
}

// 2. Обновление ключа (POST /refresh_key)
const refreshKey = async () => {
  updatingKey.value = true
  try {
    // Выполняем рефреш на бэкенде
    await axios.post(`http://localhost:8000/refresh_key/${userId}`)
    
    // Сразу запрашиваем обновленный ключ из базы
    await fetchKey()
    
    alert("Ключ успешно обновлен и отправлен на почту")
  } catch (e) {
    console.error(e)
    alert("Не удалось обновить ключ")
  } finally {
    updatingKey.value = false
  }
}

// 3. Смена пароля
const changePassword = async () => {
  try {
    // ВАЖНО: Проверь путь /change_password (в main.py было через подчеркивание)
    await axios.post('http://localhost:8000/change_password', {
      user_id: parseInt(userId),
      old_password: passwords.value.old,
      new_password: passwords.value.new,
      confirm_password: passwords.value.confirm // Или добавь отдельное поле в форму
    })
    alert('Пароль успешно изменен')
    passwords.value = { old: '', new: '' } // Очистка формы
  } catch (e) {
    alert('Ошибка: ' + (e.response?.data?.detail || 'не удалось сменить пароль'))
  }
}

const logout = () => {
  localStorage.removeItem('user_id')
  router.push('/login')
}

// При входе на страницу сразу тянем данные
onMounted(() => {
  if (!userId) {
    router.push('/login')
  } else {
    fetchKey()
  }
})
</script>