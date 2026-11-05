const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL || 'https://cmlcmbprymurbokuihsg.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtbGNtYnByeW11cmJva3VpaHNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3Mzg4NTUsImV4cCI6MjA4NTMxNDg1NX0.xq_4hoxGSCtGiVSh6lDKHRVCME_sWzXKzegbu0ao7oQ';

const supabase = createClient(supabaseUrl, supabaseKey);

async function signin() {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: 'subscribe.catalog@gmail.com',
        password: 'Joseluis_49',
    });

    if (error) {
        console.error('Error:', error.message);
    } else {
        console.log('✓ Login successful!');
        console.log('User ID:', data.user?.id);
        console.log('Email:', data.user?.email);
        console.log('Access Token:', data.session?.access_token?.substring(0, 20) + '...');
    }
}

signin();
