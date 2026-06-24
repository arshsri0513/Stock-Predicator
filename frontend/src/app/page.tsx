// This is the Home page. In Next.js App Router, a file named `page.tsx`
// inside `app/` automatically becomes a route. This file at
// `src/app/page.tsx` maps to the URL "/".
//
// Right now it's a placeholder just to confirm the skeleton runs end to end.
// Phase 10 will replace this with the real dashboard/landing page.
export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold">Stock Predictor</h1>
      <p className="mt-2 text-gray-600">
        Phase 2 skeleton — frontend is wired up and ready.
      </p>
    </main>
  );
}
