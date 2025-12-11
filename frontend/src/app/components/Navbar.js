import Image from "next/image";
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 flex items-center justify-between w-full px-8 py-4 bg-[#13120a]">
      <div className="flex items-center gap-3">
        <Link href="/">
        <Image
          src="/polysonar.png"
          alt="Logo"
          width={50}
          height={50}
          className="object-contain"
        />
        </Link>
      </div>
      <div className="flex items-center gap-8">
      <Link href="/dashboard" className="text-white hover:opacity-80 transition-opacity text-sm">
          Dashboard
        </Link>
        <Link href="/whales" className="text-white hover:opacity-80 transition-opacity text-sm">
          Whales
        </Link>
        <Link href="/alerts" className="text-white hover:opacity-80 transition-opacity text-sm">
          Alerts
        </Link>
      </div>
    </nav>
  );
}
