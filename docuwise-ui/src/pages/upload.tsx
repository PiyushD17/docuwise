import dynamic from "next/dynamic";
const UploadCard = dynamic(() => import("../components/UploadCard"), { ssr: false });
const RecentFiles = dynamic(() => import("../components/RecentFiles"), { ssr: false }); // NEW

export default function UploadPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <UploadCard />
      <RecentFiles />   {/* NEW */}
    </div>
  );
}
