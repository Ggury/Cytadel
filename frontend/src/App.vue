<template>
  <v-app>
    <v-app-bar flat border>
      <v-app-bar-title>Cytadel Proxy</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn to="/register">Регистрация</v-btn>
      <v-btn to="/login">Вход</v-btn>
      <v-btn to="/profile">Кабинет</v-btn>
    </v-app-bar>

    <v-main>
      <router-view /> 
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
</script>