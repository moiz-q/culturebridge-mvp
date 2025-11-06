import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">CultureBridge</h3>
            <p className="text-gray-400 text-sm">
              AI-powered platform connecting intercultural coaches with global professionals.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase mb-4">Platform</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/coaches" className="text-gray-400 hover:text-white text-sm">
                  Find Coaches
                </Link>
              </li>
              <li>
                <Link href="/community" className="text-gray-400 hover:text-white text-sm">
                  Community
                </Link>
              </li>
              <li>
                <Link href="/community/resources" className="text-gray-400 hover:text-white text-sm">
                  Resources
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase mb-4">Company</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  About Us
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Careers
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold uppercase mb-4">Legal</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white text-sm">
                  Cookie Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 text-center">
          <p className="text-gray-400 text-sm">
            © {new Date().getFullYear()} CultureBridge. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
