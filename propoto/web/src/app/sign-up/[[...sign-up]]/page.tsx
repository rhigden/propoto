import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Propoto
                    </h1>
                    <p className="text-gray-400 mt-2">Create your account</p>
                </div>
                <SignUp 
                    appearance={{
                        elements: {
                            rootBox: "mx-auto",
                            card: "bg-black/40 backdrop-blur-xl border border-white/10",
                        }
                    }}
                    routing="path"
                    path="/sign-up"
                    signInUrl="/sign-in"
                    forceRedirectUrl="/dashboard"
                />
            </div>
        </div>
    );
}

