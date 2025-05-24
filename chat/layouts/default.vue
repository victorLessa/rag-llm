<template>
  <div class="layout">
    <AppAside />

    <div class="content-area">
      <AppHeader />
      <main class="main-content">
        <slot />
      </main>
      <footer class="footer">
        © 2025 Chat FAQ. Todos os direitos reservados.
      </footer>
    </div>
  </div>
</template>

<script lang="ts" setup>
import AppAside from '~/layouts/AppAside.vue';
import AppHeader from '~/layouts/AppHeader.vue';
// ...existing code...
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #181a20;
  color: #f1f1f1;
}

.content-area {
  flex: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #181a20;
}

.main-content {
  flex: 1;
  padding: 1rem;
  background: #22232b;
  border-radius: 12px;
  margin: .5rem 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
}

.footer {
  padding: 1rem 2rem;
  text-align: center;
  background: #181a20;
  color: #888;
  font-size: 0.95rem;
  border-top: 1px solid #23262f;
  border-radius: 0 0 12px 12px;
  margin: 0 1rem 1rem 1rem;
}

:deep(header) {
  background: transparent;
}
</style>