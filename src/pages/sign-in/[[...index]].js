import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return <SignIn routing="hash" path="/sign-in" />;
}
