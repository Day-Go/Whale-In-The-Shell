using Supabase;
using Supabase.Gotrue;
using Supabase.Interfaces;
using Supabase.Realtime;
using Supabase.Storage;

public class SupabaseService
{
    private readonly Supabase.Client _supabaseClient;

    public SupabaseService(string url, string key)
    {
        var options = new SupabaseOptions
        {
            AutoConnectRealtime = true
        };

        _supabaseClient = new Supabase.Client(url, key, options);
    }

    public async Task<ISupabaseClient<User, Session, RealtimeSocket, RealtimeChannel, Bucket, FileObject>> GetClientAsync()
    {
        return await _supabaseClient.InitializeAsync();
    }
}
