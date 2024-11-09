from .models import PartnerInfo

def partner_profile_picture(request):
    if request.session.get('partner_id'):
        try:
            partner_info = PartnerInfo.objects.get(partner_id=request.session['partner_id'])
            profile_picture_url = partner_info.profile_picture.url if partner_info.profile_picture else 'default_profile_pic_url'
        except PartnerInfo.DoesNotExist:
            profile_picture_url = 'default_profile_pic_url'
    else:
        profile_picture_url = 'default_profile_pic_url'

    return {
        'partner_profile_picture_url': profile_picture_url
    }