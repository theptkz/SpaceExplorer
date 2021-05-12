import pygame
from sys import exit
from random import randint

from .objects import *


pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()


def init(screen, base_dir, config, msg):
    bg = Background(screen, base_dir, 0, 0)
    plate = SpacePlate(screen, base_dir, config)
    score = Score(screen, base_dir, msg)
    end = End(screen, base_dir, config)
    pause = Pause(screen, base_dir, config)

    return bg, plate, score, end, pause


def check_events(screen,config, base_dir, plate, astrs, boosts, bullet, end, pause, play, table, settings):
    if config['sub_scene'] == 'game':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                config['sub_scene'] = 'pause'

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if plate.rect.top >= plate.screen_rect.top + 50 and not plate.flip:
                    if config['user']['effects'] and plate.jump == 10:
                        pygame.mixer.Sound(plate.sounds['jump']).play()
                    plate.is_jump = True
                elif plate.rect.bottom <= plate.screen_rect.bottom - 50 and plate.flip:
                    if config['user']['effects'] and plate.jump == 10:
                        pygame.mixer.Sound(plate.sounds['jump']).play()
                    plate.is_jump = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for boost in boosts:
                    if boost.name =='bullet' and boost.is_active:
                        bl = Bullet(screen, base_dir, config, plate, True)
                        bullet.add(bl)

    elif config['sub_scene'] == 'end': 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
 
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                play.to_bottom = True
                table.to_top = True
                settings.to_top = True
                config['sub_scene'] = 'game'
                config['scene'] = 'lobby'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if end.buttons.sprites()[0]._rect.collidepoint((x, y)):
                    print('click lobby!')
                    play.to_bottom = True
                    table.to_top = True
                    settings.to_top = True

                    config['score'] = 0
                    config['sub_scene'] = 'game'
                    config['scene'] = 'lobby'

                elif end.buttons.sprites()[1]._rect.collidepoint((x, y)):
                    print('click again!')
                    config['score'] = 0
                    config['sub_scene'] = 'game'
                    config['scene'] = 'game'

    elif config['sub_scene'] == 'pause':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                config['sub_scene'] = 'game'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if pause.buttons.sprites()[0]._rect.collidepoint((x, y)):
                    print('click lobby!')
                    play.to_bottom = True
                    table.to_top = True
                    settings.to_top = True

                    plate.reset()
                    astrs.empty()
                    boosts.empty()
                    config['speed'] = 2
                    config['score'] = 0
                    config['sub_scene'] = 'game'
                    config['scene'] = 'lobby'

                elif pause.buttons.sprites()[1]._rect.collidepoint((x, y)):
                    print('click resume!')
                    config['sub_scene'] = 'game'


def spawn(screen, base_dir, config, tick, plate, astrs, boosts):
    if len(astrs) == 0 or astrs.sprites()[-1].rect.x < config['mode'][0] - 200:
        astrs.add(Asteroid(screen, base_dir, config))

    # Spawn flying asteroid if difficulty >= middle
    if config['score'] >= 10 and config['score'] % 5 == 0 and config['user']['difficulty'] >= 1:
        for sprite in astrs.copy():
            if sprite.name == 'flying':
                break
        else:
            astrs.add(FlyingAsteroid(screen, base_dir, config))

    if len(boosts) == 0:
        max_choice = 3

        # Spawn mirror boost if difficulty >= hard
        if config['user']['difficulty'] >= 2: max_choice += 1
        choice = randint(0, max_choice)

        if choice == 0:
            boost = TimeBoost(screen, base_dir, config)
        elif choice == 1:
            boost = DoubleBoost(screen, base_dir, config)
        elif choice == 2:
            boost = ShieldBoost(screen, base_dir, config, plate)
        elif choice == 3:
            boost = BulletBoost(screen,base_dir, config, plate)
        elif choice == 4:
            boost = MirrorBoost(screen, base_dir, config, plate)

        while pygame.sprite.spritecollideany(boost, astrs):
            if choice == 0:
                boost = TimeBoost(screen, base_dir, config)
            elif choice == 1:
                boost = DoubleBoost(screen, base_dir, config)
            elif choice == 2:
                boost = ShieldBoost(screen, base_dir, config, plate)
            elif choice == 3:
                boost = BulletBoost(screen,  base_dir, config, plate)    
            elif choice == 4:
                boost = MirrorBoost(screen, base_dir, config, plate)

        boosts.add(boost)


def update(screen, config, base_dir, bg, plate, astrs, boosts, bullet, score, end, pause, tick):
    if config['sub_scene'] == 'game':
        if tick % 2 == 0:
            bg.update()

        bg.blit()

        if tick % (config['FPS'] * 7) == 0:
            for boost in boosts.sprites():
                if boost.name == 'time' and boost.is_active:
                    boost.speed += 1
                    break
            else:
                config['speed'] += 1

        spawn(screen, base_dir, config, tick, plate, astrs, boosts)

        for astr in astrs.copy():
            if astr.rect.right < 5 or astr.rect.top > config['mode'][1]:
                astrs.remove(astr)
                if config['user']['effects']:
                    pygame.mixer.Sound(plate.sounds['score']).play()

                for boost in boosts.copy():
                    if boost.name == 'double' and boost.is_active:
                        config['score'] += 2
                    else:
                        config['score'] += 1

        for astr in astrs.sprites():
            astr.update() 
            astr.blit()

        plate.update()

        for boost in boosts.sprites():
            boost.update()
            boost.blit()

        for bl in bullet.sprites():
            bl.update()
            bl.blit()

        score.msg = f"score: {config['score']}"
        score.update()
        score.blit()

        plate.blit()

    elif config['sub_scene'] == 'end':
        bg.blit()

        end.update()
        end.blit()

    elif config['sub_scene'] == 'pause':
        bg.blit()

        pause.update()
        pause.blit()


def check_collides(screen, config, base_dir, astrs, boosts, plate, bullet, play, table, settings, score):
    astrs_collides = pygame.sprite.spritecollide(plate, astrs, True)
    boosts_collides = pygame.sprite.spritecollide(plate, boosts, False)
    bullet_collides = pygame.sprite.groupcollide(astrs, bullet, True, True)

    if astrs_collides:
        if config['user']['effects']:
            pygame.mixer.Sound(plate.sounds['bang']).play()
    
        for boost in boosts:
            if boost.name == 'shield' and boost.is_active:
                boosts.remove(boost)
                break
        else:
            with open(f'{base_dir}/config/score.csv', 'a') as file:
                line = ','.join([str(config['score']), config['user']['nick']]) + '\n'
                file.write(line)

            score.is_update = True

            plate.reset()
            astrs.empty()
            boosts.empty()
            bullet.empty()

            config['speed'] = 2
            config['sub_scene'] = 'end'

    elif boosts_collides and not boosts_collides[0].is_active:
        boost = boosts_collides[0]

        if boost.name == 'time':
            boost.is_active = True
            boost.speed = config['speed']
            config['speed'] = 2

        elif boost.name == 'double':
            boost.is_active = True

        elif boost.name == 'shield':
            boost.is_active = True

        elif boost.name == 'bullet':
            boost.is_active = True

        elif boost.name == 'mirror':
            boost.is_active = True
            plate.rect.y += 24
            plate.flip = True
    
    elif bullet_collides:
        if config['user']['effects']:
            pygame.mixer.Sound(plate.sounds['bang']).play()
        config['score']+=1
        
    
    elif (plate.rect.bottom >= plate.screen_rect.bottom and not plate.flip) or (plate.rect.top <= plate.screen_rect.top and plate.flip):
        if config['user']['effects']:
            pygame.mixer.Sound(plate.sounds['bang']).play()

        for boost in boosts:
            if boost.name == 'shield' and boost.is_active:
                boosts.remove(boost)
                plate.is_jump = True
                break
        else:
            with open(f'{base_dir}/config/score.csv', 'a') as file:
                line = ','.join([str(config['score']), config['user']['nick']]) + '\n'
                file.write(line)

            score.is_update = True

            plate.reset()
            astrs.empty()
            boosts.empty()
            bullet.empty()

            config['speed'] = 2
            config['sub_scene'] = 'end'
        
        

