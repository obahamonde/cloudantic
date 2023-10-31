<template>
  <nav flex="~ gap-4" mt-6 justify-center text-xl>
    <RouterLink icon-btn to="/" title="Home" data-test-id="home">
      <Icon icon="mdi-home" />
    </RouterLink>

    <button icon-btn @click="toggleDark()" title="Toggle Theme">
      <Icon :icon="isDark ? 'mdi-lightbulb-off' : 'mdi-lightbulb-on'" />
    </button>

    <RouterLink icon-btn to="/about" title="About" data-test-id="about">
      <Icon icon="mdi-information" />
    </RouterLink>

    <a
      icon-btn
      rel="noreferrer"
      href="https://github.com/obahamonde/aiofauna"
      target="_blank"
      title="GitHub"
    >
      <Icon icon="mdi-github" />
    </a>
  </nav>
</template>
