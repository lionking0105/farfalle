import Link from "next/link";
import { Button } from "./ui/button";
import { SiX, SiGithub } from "react-icons/si";

export function Footer() {
  return (
    <footer className="w-full flex fixed bottom-0 right-0 p-1 z-50">
      <div className="px-1 w-full flex flex-row justify-end space-x-1">
        <Button variant="ghost" size="icon" className="hover:bg-transparent">
          <Link href="https://git.new/farfalle" target="_blank">
            <SiGithub size={16} />
          </Link>
        </Button>
        <Link href="https://x.com/rashadphz" target="_blank">
          <Button variant="ghost" size="icon" className="hover:bg-transparent">
            <SiX size={16} />
          </Button>
        </Link>
      </div>
    </footer>
  );
}
