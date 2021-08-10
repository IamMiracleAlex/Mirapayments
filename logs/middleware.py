import logging

from django.utils.deprecation import MiddlewareMixin

db_logger = logging.getLogger('db')


class LogMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        # Log the exception details
        db_logger.exception(exception)


        # if not settings.DEBUG:
            
        #     #Notify on slack
        #     #TODO: Make request async (to make request processing faster)
        #     main_text = "Mirapayments API has reported an error!"

        #     data = {
        #         'payload': json.dumps({'text': main_text, 'attachments': make_attachment(request, exception)}),
        #     }
        #     webhook_url = "https://hooks.slack.com/services/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"
        #     r = requests.post(webhook_url, data=data)

        return None