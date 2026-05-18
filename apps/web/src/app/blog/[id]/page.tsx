import { redirect } from 'next/navigation';
import BlogPostPage from '../../../screens/BlogPostPage';
import { blogPosts } from '../../../data/blog';

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!blogPosts.some((post) => post.id === id)) redirect('/blog');
  return <BlogPostPage id={id} />;
}
