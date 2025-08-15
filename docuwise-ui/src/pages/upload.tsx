import dynamic from "next/dynamic";
const UploadCard = dynamic(() => import("../components/UploadCard"), { ssr: false });
const RecentUploads = dynamic(() => import("../components/RecentUploads"), { ssr: false });

export default function UploadPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <UploadCard />
      <RecentUploads />
    </div>
  );
}
