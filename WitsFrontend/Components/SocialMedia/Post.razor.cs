using Radzen;
using Supabase.Gotrue;
using Supabase.Interfaces;
using Supabase.Realtime;
using Supabase.Storage;
using WitsFrontend.Models;

namespace WitsFrontend.Components.SocialMedia;


public partial class Post
{
    private ISupabaseClient<User, Session, RealtimeSocket, RealtimeChannel, Bucket, FileObject> _supabaseClient;

    List<Agent> agents; // Use nullable reference type for agent variable

    protected override async Task OnInitializedAsync()
    {
        _supabaseClient = await supabaseService.GetClientAsync();

        var response = await _supabaseClient.From<Agent>().Get();
        agents = response.Models;

        if (agents == null)
        {
            // Return fail state
            return;
        }
    }
}
