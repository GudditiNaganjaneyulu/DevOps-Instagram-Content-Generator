import { Sidebar } from "@/components/Sidebar";

export default function PrivateLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      {/* pt-16 on mobile gives space below the fixed hamburger button */}
      <main className="flex-1 overflow-auto p-4 pt-16 md:p-6 md:pt-6">
        {children}
      </main>
    </div>
  );
}
