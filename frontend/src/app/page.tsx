import Hero from "@/components/Hero";
import WhyChoose from "@/components/WhyChoose";
import Models from "@/components/Models";

export default function HomePage() {
  return (
    <main className="min-h-screen">

      <Hero />

      <WhyChoose />

      <Models />

      <footer
        className="border-t py-6 text-center text-sm"
        style={{
          borderColor: "var(--border-subtle)",
          color: "var(--text-secondary)",
        }}
      >
        © 2026 <strong>StockPredict</strong> • Developed by{" "}
        <span
          className="font-semibold"
          style={{ color: "var(--accent-primary)" }}
        >
          Arsh Srivastava
        </span>
      </footer>

    </main>
  );
}