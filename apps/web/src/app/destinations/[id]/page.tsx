import { redirect } from 'next/navigation';
import CountryDetailPage from '../../../screens/CountryDetailPage';
import { countries } from '../../../data/countries';

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!countries.some((country) => country.id === id)) redirect('/destinations');
  return <CountryDetailPage id={id} />;
}
