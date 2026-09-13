import type { MetadataRoute } from "next";
export default function manifest(): MetadataRoute.Manifest {
  return {
    id: "/",
    name: "Luma",
    short_name: "Luma",
    description: "A little space for your tasks, thoughts, and time.",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#f8f7f2",
    theme_color: "#182b2a",
    icons: [
      {
        src: "/icons/luma-192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/luma-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/luma-maskable-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
