<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-[#232223] text-white text-center px-6">
    <h1 class="text-3xl font-semibold mb-6 text-[#ff9100]">K.I.T. Solutions</h1>
    <p class="mb-8 text-white/70">Unsere wichtigsten Links auf einen Blick 👇</p>

    <div class="flex flex-col gap-4 w-full max-w-sm">
      <a
        href="https://kit-it-koblenz.de"
        target="_blank"
        class="w-full py-3 rounded-xl border-2 border-[#ff9100] text-white hover:bg-[#ff9100] hover:text-[#232223] transition"
      >
        🌐 Webseite
      </a>

      <a
        href="https://www.instagram.com/kit.koblenz"
        target="_blank"
        class="w-full py-3 rounded-xl border-2 border-[#ff9100] text-white hover:bg-[#ff9100] hover:text-[#232223] transition"
      >
        📸 Instagram
      </a>

      <a
        href="mailto:info@kit-it-koblenz.de"
        class="w-full py-3 rounded-xl border-2 border-[#ff9100] text-white hover:bg-[#ff9100] hover:text-[#232223] transition"
      >
        ✉️ E-Mail schreiben
      </a>
    </div>

    <footer class="absolute bottom-4 text-xs text-white/40">
      © {{ new Date().getFullYear() }} K.I.T. Solutions · IT muss nicht schmutzig sein.
    </footer>
  </div>
</template>

<script setup lang="ts">
// keine Logik nötig
</script>
