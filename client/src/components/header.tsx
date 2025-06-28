import { Button } from "@/components/ui/button";
import { GraduationCap, Menu, User } from "lucide-react";
import { Link } from "wouter";

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-neutral-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-neutral-900 flex items-center">
                <GraduationCap className="text-primary mr-2" size={28} />
                EduVideoAI
              </h1>
            </Link>
          </div>
          <nav className="hidden md:block">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-neutral-600 hover:text-primary transition-colors">
                Home
              </Link>
              <Link href="/series" className="text-neutral-600 hover:text-primary transition-colors">
                My Series
              </Link>
              <Link href="/library" className="text-neutral-600 hover:text-primary transition-colors">
                Library
              </Link>
              <Button className="bg-primary text-white hover:bg-blue-600">
                <User className="mr-2" size={16} />
                Account
              </Button>
            </div>
          </nav>
          <Button variant="ghost" className="md:hidden text-neutral-600">
            <Menu size={20} />
          </Button>
        </div>
      </div>
    </header>
  );
}
