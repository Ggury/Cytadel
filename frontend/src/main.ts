import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router' // Импортируем созданный роутер

const app = createApp(App)

app.use(vuetify)
app.use(router) // Подключаем роутер к приложению

app.mount('#app')