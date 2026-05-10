import Spinner from "@/components/ui/Spinner";

export default function Loading() {
  return (
    <div className="container-page py-20 flex items-center justify-center min-h-[50vh]">
      <Spinner size="lg" label="Caricamento..." />
    </div>
  );
}
